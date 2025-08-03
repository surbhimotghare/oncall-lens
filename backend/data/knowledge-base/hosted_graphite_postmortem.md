# Hosted Graphite Postmortem Report (#2)

## Outage
**Period:** March 12th 2014 18:50 UTC to 19:20 (30 minutes)  
**Impact:** Complete loss of new incoming data from all customers in the shared environment on all interfaces (UDP, TCP, TCP python pickle, HTTP)  
**Additional Impact:** Significant frontend graph rendering latency, Frontend HTTP 500 errors

## Timeline (all times are UTC, which is also local for the responding engineers)

**18:46:** A user, still sending data to us, deletes their account.

**18:50:** All 13 aggregation services attempt to remove some data for this user from a queue, but a lookup on the user's ID fails. Queue processing stops, and it starts building up in memory. No new metric data is written out.

**18:56:** PagerDuty fires an alert and calls the on-call engineer.

**18:56:** The on call engineer begins investigating.

**19:00:** The first outage notification tweet is sent.

**19:10:** After spending ten minutes investigating and attempting to recover the service, a decision is made to discard a large amount of data in memory in order to get the service back up and running quickly. The discarded data is copied in logs that can be replayed.

**19:20:** The service is operating normally, but large chunks of recent data are missing from graphs.

**19:30:** The on call engineer begins replaying a portion of the logs to restore the missing data, while a second engineer begins looking for the root cause. Normally we'd wait a bit before doing root cause analysis, but without a good understanding of the cause we felt it could happen again soon.

**20:57:** Half of the restore has been completed.

**22:00:** All restores complete. The only missing data is that which was lost during the actual outage, which lasted for 30 minutes.

## Actions already taken
We have added better error handling to the aggregation services to fix this condition.

## Plan
1) While we were able to replay logs to restore some data, we didn't record enough to allow us to replay everything. We've had a project planned for a few months to record everything and hopefully allow complete recovery from outages, and we've changed some project priorities to get that work started next week.

2) We still plan to publish an offsite status page to help keep customers informed during events like this.

## Conclusion
We always regret losing data, it sucks and we're sorry we failed this time.

Being able to replay logs to recover from a failure is a pretty powerful tool. It helped make the decision to discard some data in order to recover the service faster, and we think that with more logging of incoming data that we'll be in a better position the next time we have an outage like this. 