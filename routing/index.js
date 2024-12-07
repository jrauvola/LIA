const express = require('express');
const app = express();

// Counter for visitors (note: this resets when the service restarts)
let totalVisitors = 0;

// Generate 10 service URLs with new naming scheme
const SERVICE_URLS = Array.from({ length: 10 }, (_, i) => {
  return `https://liamockinterview${i + 1}-945640430357.us-central1.run.app`;
});

function assignUserToService() {
  // Increment visitor count
  totalVisitors++;
  
  // Calculate which service to use (cycling through 0-9)
  const serviceIndex = (totalVisitors - 1) % 10;
  const serviceUrl = SERVICE_URLS[serviceIndex];
  
  return {
    serviceUrl,
    visitorNumber: totalVisitors,
    serviceIndex: serviceIndex + 1  // Adding 1 for human-readable numbering
  };
}

// Main routing logic
app.get('/', (req, res) => {
  try {
    const assignment = assignUserToService();
    
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