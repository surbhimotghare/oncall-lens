"""
Synthetic Dataset Generator for RAGAS Evaluation
Generates question-context-answer-ground_truth tuples from historical postmortems.
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema import Document
from pydantic import BaseModel, Field

from config.settings import Settings

logger = logging.getLogger(__name__)


class SyntheticQA(BaseModel):
    """Model for synthetic Q&A pairs."""
    question: str = Field(description="The generated question about the incident")
    answer: str = Field(description="The expected answer based on the postmortem")
    ground_truth: str = Field(description="The ground truth answer for evaluation")
    context: str = Field(description="The relevant context from the postmortem")
    category: str = Field(description="Category of question (root_cause, resolution, impact, etc.)")


class DatasetGenerator:
    """
    Generates synthetic evaluation datasets from historical postmortems.
    
    This class uses LLM-powered data generation to create realistic questions
    that an on-call engineer might ask during an incident, along with the
    expected answers based on historical postmortem data.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=settings.openai_api_key
        )
        self.parser = JsonOutputParser(pydantic_object=SyntheticQA)
        
        # Question generation templates for different categories
        self.question_templates = {
            "root_cause": [
                "What was the root cause of the {incident_type} incident?",
                "Why did the {service_name} fail?",
                "What caused the {failure_mode} in {date}?",
                "What was the underlying issue that led to this outage?"
            ],
            "resolution": [
                "How was the {incident_type} incident resolved?",
                "What steps were taken to fix the {service_name} issue?",
                "How did the team restore service during the {failure_mode}?",
                "What was the fix for the {incident_date} incident?"
            ],
            "impact": [
                "What was the impact of the {incident_type} incident?",
                "How many users were affected by the {service_name} outage?",
                "What was the business impact of the {failure_mode}?",
                "How long did the {incident_date} incident last?"
            ],
            "prevention": [
                "How could the {incident_type} incident have been prevented?",
                "What preventive measures were recommended after the {service_name} failure?",
                "What action items came out of the {failure_mode} postmortem?",
                "What monitoring improvements were suggested?"
            ],
            "detection": [
                "How was the {incident_type} incident detected?",
                "What alerts fired during the {service_name} outage?",
                "How did the team first notice the {failure_mode}?",
                "What monitoring detected this issue?"
            ]
        }
        
    async def load_postmortems(self, knowledge_base_path: str) -> List[Document]:
        """Load all postmortem documents from the knowledge base."""
        logger.info(f"Loading postmortems from {knowledge_base_path}")
        
        kb_path = Path(knowledge_base_path)
        postmortems = []
        
        for file_path in kb_path.glob("*.md"):
            if file_path.name.startswith("postmortem-template"):
                continue  # Skip template files
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            doc = Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "filename": file_path.name,
                    "type": "postmortem"
                }
            )
            postmortems.append(doc)
            
        logger.info(f"Loaded {len(postmortems)} postmortem documents")
        return postmortems
    
    def extract_incident_details(self, postmortem_content: str) -> Dict[str, str]:
        """Extract key details from postmortem for template filling."""
        lines = postmortem_content.split('\n')
        details = {
            "incident_type": "system failure",
            "service_name": "service",
            "failure_mode": "outage",
            "incident_date": "unknown date"
        }
        
        # Extract title/summary information
        for line in lines[:20]:  # Check first 20 lines
            line_lower = line.lower()
            if '# ' in line and 'postmortem' in line_lower:
                title = line.replace('#', '').strip()
                if 'database' in title.lower():
                    details["incident_type"] = "database failure"
                    details["service_name"] = "database"
                elif 'search' in title.lower():
                    details["incident_type"] = "search failure"
                    details["service_name"] = "search service"
                elif 'api' in title.lower():
                    details["incident_type"] = "API failure"
                    details["service_name"] = "API"
                    
        return details
    
    async def generate_questions_for_postmortem(
        self, 
        postmortem: Document,
        num_questions_per_category: int = 2
    ) -> List[SyntheticQA]:
        """Generate synthetic Q&A pairs for a single postmortem."""
        
        content = postmortem.page_content
        incident_details = self.extract_incident_details(content)
        
        synthetic_qas = []
        
        for category, templates in self.question_templates.items():
            for i in range(min(num_questions_per_category, len(templates))):
                template = templates[i % len(templates)]
                
                # Create the question generation prompt
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are an expert at creating realistic questions that on-call engineers would ask during incident response. 

Given a postmortem document, generate a specific, realistic question that an engineer might ask about this incident, along with the expected answer based on the postmortem content.

The question should be:
1. Specific to the incident described
2. Something an on-call engineer would actually ask
3. Answerable from the postmortem content
4. In the category: {category}

Return your response as valid JSON matching this schema:
{format_instructions}"""),
                    ("human", """Postmortem Document:
{postmortem_content}

Category: {category}
Question Template: {template}

Generate a realistic question and answer based on this postmortem.""")
                ])
                
                formatted_prompt = prompt.format(
                    category=category,
                    postmortem_content=content[:3000],  # Truncate for token limits
                    template=template.format(**incident_details),
                    format_instructions=self.parser.get_format_instructions()
                )
                
                try:
                    response = await self.llm.ainvoke(formatted_prompt)
                    qa_data = self.parser.parse(response.content)
                    
                    # Enhance the generated data
                    qa_data.context = content[:2000]  # Use first 2000 chars as context
                    qa_data.category = category
                    
                    synthetic_qas.append(qa_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to generate Q&A for {category}: {e}")
                    continue
                    
        return synthetic_qas
    
    async def generate_full_dataset(
        self, 
        knowledge_base_path: str,
        output_path: str,
        num_questions_per_category: int = 2
    ) -> Dict[str, Any]:
        """Generate a complete synthetic evaluation dataset."""
        
        logger.info("Starting synthetic dataset generation...")
        
        # Load postmortems
        postmortems = await self.load_postmortems(knowledge_base_path)
        
        if not postmortems:
            raise ValueError("No postmortem documents found in knowledge base")
        
        all_synthetic_qas = []
        
        # Generate Q&As for each postmortem
        for i, postmortem in enumerate(postmortems):
            logger.info(f"Processing postmortem {i+1}/{len(postmortems)}: {postmortem.metadata['filename']}")
            
            try:
                qas = await self.generate_questions_for_postmortem(
                    postmortem, 
                    num_questions_per_category
                )
                all_synthetic_qas.extend(qas)
                
                # Small delay to avoid rate limits
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to process {postmortem.metadata['filename']}: {e}")
                continue
        
        # Create the final dataset
        dataset = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_questions": len(all_synthetic_qas),
                "source_postmortems": len(postmortems),
                "categories": list(self.question_templates.keys()),
                "generator_version": "1.0.0"
            },
            "questions": [],
            "contexts": [],
            "answers": [],
            "ground_truths": []
        }
        
        # Format for RAGAS
        for qa in all_synthetic_qas:
            dataset["questions"].append(qa.question)
            dataset["contexts"].append([qa.context])  # RAGAS expects list of contexts
            dataset["answers"].append(qa.answer)
            dataset["ground_truths"].append(qa.ground_truth)
        
        # Save dataset
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated dataset with {len(all_synthetic_qas)} Q&A pairs saved to {output_path}")
        
        return dataset


async def main():
    """Generate a synthetic dataset for evaluation."""
    from config.settings import get_settings
    
    settings = get_settings()
    generator = DatasetGenerator(settings)
    
    knowledge_base_path = "backend/data/knowledge-base"
    output_path = "backend/evaluation/data/synthetic_dataset.json"
    
    dataset = await generator.generate_full_dataset(
        knowledge_base_path=knowledge_base_path,
        output_path=output_path,
        num_questions_per_category=3
    )
    
    print(f"✅ Generated dataset with {dataset['metadata']['total_questions']} questions")
    print(f"📁 Saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main()) 