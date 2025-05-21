const puppeteer = require('puppeteer');

async function checkWebApp() {
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  
  console.log('Opening app...');
  await page.goto('http://localhost:3003');
  
  await page.waitForTimeout(2000);
  
  // Dapatkan teks yang ditampilkan pada elemen health status
  const healthStatusElement = await page.;
  const healthStatus = healthStatusElement ? await page.evaluate(el => el.textContent, healthStatusElement) : 'Not found';
  
  const activeDevicesElement = await page.;
  const activeDevices = activeDevicesElement ? await page.evaluate(el => el.textContent, activeDevicesElement) : 'Not found';
  
  console.log('Health Status displayed in UI:', healthStatus);
  console.log('Active Devices displayed in UI:', activeDevices);
  
  await browser.close();
}

checkWebApp().catch(console.error);
