// Simple test script to demonstrate progress tracking
const EventSource = require('eventsource');

async function testProgress() {
  console.log('🚀 Starting progress test...');
  
  // First, start a progress stream
  const taskId = 'test-progress-' + Date.now();
  const eventSource = new EventSource(`http://localhost:8000/progress/${taskId}`);
  
  eventSource.onmessage = (event) => {
    const update = JSON.parse(event.data);
    console.log(`📊 Progress: ${update.percentage}% - ${update.message}`);
    
    if (update.completed) {
      console.log('✅ Progress completed!');
      eventSource.close();
    }
  };
  
  eventSource.onerror = (error) => {
    console.error('❌ Progress stream error:', error);
    eventSource.close();
  };
  
  // Wait a moment, then trigger the analysis
  setTimeout(async () => {
    console.log('📁 Uploading test file...');
    
    const formData = new FormData();
    const file = new File(['test log content'], 'test.log', { type: 'text/plain' });
    formData.append('files', file);
    
    try {
      const response = await fetch('http://localhost:8000/summarize', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      console.log('📋 Analysis result received');
    } catch (error) {
      console.error('❌ Analysis failed:', error);
    }
  }, 1000);
}

testProgress(); 