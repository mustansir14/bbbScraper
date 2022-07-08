<<<<<<< HEAD
=======
#!/bin/bash

echo "Close all processes marked by 'grabber-bbb-mustansir'"
ps aux | grep "grabber-bbb-mustansir" | awk '{print $2}' | xargs -r kill -9

echo "Done"
>>>>>>> f3bcc7caf9f287968abfcaecf573e440a86c1723
