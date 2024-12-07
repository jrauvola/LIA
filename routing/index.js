const express = require('express');
const { Firestore } = require('@google-cloud/firestore');

const app = express();
const firestore = new Firestore();

// Generate 10 service URLs instead of 6
const SERVICE_URLS = Array.from({ length: 10 }, (_, i) => {
  const suffix = i === 0 ? '' : `_${i + 1}`;
  return `https://liamockinterview${suffix}-945640430357.us-central1.run.app`;
});

async function assignUserToService() {
  const counterRef = firestore.collection('service-assignments').doc('counter');

  try {
    const result = await firestore.runTransaction(async (transaction) => {
      const counterDoc = await transaction.get(counterRef);
      let totalVisitors = counterDoc.exists ? counterDoc.data().totalVisitors : 0;
      
      totalVisitors++;
      
      // Calculate which service to use (cycling through 0-9 instead of 0-5)
      const serviceIndex = (totalVisitors - 1) % 10;
      const serviceUrl = SERVICE_URLS[serviceIndex];
      
      transaction.set(counterRef, { 
        totalVisitors,
        lastAssignedService: serviceIndex,
        lastAssignedAt: new Date()
      });

      return {
        serviceUrl,
        visitorNumber: totalVisitors,
        serviceIndex: serviceIndex + 1  // Adding 1 for human-readable numbering
      };
    });

    return result;
  } catch (error) {
    console.error('Error in assignUserToService:', error);
    return null;
  }
}

// Main routing logic
app.get('/', async (req, res) => {
  try {
    const assignment = await assignUserToService();
    
    if (!assignment) {
      res.status(500).send('Error assigning service');
      return;
    }

    res.send(`
      <html>
        <body>
          <h2>Welcome Visitor #${assignment.visitorNumber}!</h2>
          <p>You are being redirected to Service #${assignment.serviceIndex}</p>
          <p>Redirecting to: ${assignment.serviceUrl}</p>
          <script>
            setTimeout(() => {
              window.location.href = '${assignment.serviceUrl}';
            }, 3000);
          </script>
        </body>
      </html>
    `);

  } catch (error) {
    console.error('Error handling request:', error);
    res.status(500).send('Internal server error');
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Router service listening on port ${PORT}`);
  console.log('Available services:', SERVICE_URLS);
});