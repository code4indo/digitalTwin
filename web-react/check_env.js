console.log('API KEY from environment:', process.env.REACT_APP_API_KEY || 'Not set');

// Check if the environment is properly set up for the Digital Twin React app

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

console.log('=== Digital Twin Environment Check ===');

// Check for required environment variables
const requiredEnvVars = ['REACT_APP_API_URL', 'REACT_APP_API_KEY'];
const missingVars = [];

requiredEnvVars.forEach(varName => {
  if (!process.env[varName]) {
    missingVars.push(varName);
  }
});

if (missingVars.length > 0) {
  console.warn(`⚠️ Missing environment variables: ${missingVars.join(', ')}`);
  console.log('   Creating .env.local file with default values...');
  
  // Create default .env.local file
  const defaultEnv = [
    'REACT_APP_API_URL=http://localhost:8002',
    'REACT_APP_API_KEY=development_key_for_testing'
  ].join('\n');
  
  fs.writeFileSync(path.join(__dirname, '.env.local'), defaultEnv);
  console.log('✅ Created .env.local with default values');
} else {
  console.log('✅ All required environment variables are set');
}

// Check API connection
const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8002';
console.log(`Checking API connection at ${apiUrl}/health...`);

const httpModule = apiUrl.startsWith('https') ? https : http;
const apiKey = process.env.REACT_APP_API_KEY || 'development_key_for_testing';

const requestOptions = {
  headers: {
    'X-API-Key': apiKey
  },
  timeout: 5000
};

// Try to connect to API
new Promise((resolve, reject) => {
  const req = httpModule.get(`${apiUrl}/health`, requestOptions, (res) => {
    if (res.statusCode === 200) {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve(response);
        } catch (err) {
          reject(new Error(`Invalid API response format: ${err.message}`));
        }
      });
    } else {
      reject(new Error(`API returned status code ${res.statusCode}`));
    }
  });

  req.on('error', (err) => {
    reject(err);
  });

  req.on('timeout', () => {
    req.destroy();
    reject(new Error('API request timed out'));
  });
})
.then(response => {
  console.log('✅ API connection successful!');
  console.log(`   API Status: ${response.status}`);
  console.log(`   API Version: ${response.version || 'unknown'}`);
})
.catch(err => {
  console.warn(`⚠️ API connection failed: ${err.message}`);
  console.log('   The React app will still start, but may not function properly without API access.');
  console.log('   Consider running the API separately with: python api.py');
})
.finally(() => {
  console.log('=== Environment check completed ===');
});
