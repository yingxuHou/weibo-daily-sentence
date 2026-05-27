# Zeabur MySQL Connection Troubleshooting

## Connection Details
- **Host**: 47.84.57.156
- **Port**: 31910
- **User**: root
- **Password**: N81P265Ru7ODZkp0VQz943GMibgExJqK
- **Database**: zeabur

## Current Issue
Connection fails with error: `(2013, 'Lost connection to MySQL server during query')`

## Possible Causes & Solutions

### 1. Network/Firewall Issue
**Check**: Is the port accessible from your network?
```bash
# Test with telnet or PowerShell
Test-NetConnection -ComputerName 47.84.57.156 -Port 31910
```

**Solution**: 
- Check if you're behind a corporate firewall
- Try from a different network
- Contact Zeabur support to verify port accessibility

### 2. IP Whitelist Required
**Check**: Does Zeabur require IP whitelisting?

**Solution**:
1. Go to Zeabur dashboard
2. Find MySQL service settings
3. Add your public IP to the whitelist
4. Get your public IP: https://api.ipify.org

### 3. SSL/TLS Required
**Check**: Does Zeabur require SSL connections?

**Solution**: Update DATABASE_URL to include SSL parameters:
```
DATABASE_URL=mysql+pymysql://root:PASSWORD@47.84.57.156:31910/zeabur?charset=utf8mb4&ssl_ca=&ssl_disabled=false
```

### 4. Connection Timeout
**Current setting**: 30 seconds timeout added

**Try**: Increase timeout or test from server location closer to Zeabur

## Recommended Next Steps

1. **Check Zeabur Dashboard**:
   - Look for connection examples/documentation
   - Check if there's a "Connect" button with specific instructions
   - Verify the service is running and healthy

2. **Test from Zeabur's Network**:
   - Deploy a simple test script to Zeabur
   - Test connection from within Zeabur's network
   - This will confirm if it's a network accessibility issue

3. **Alternative: Deploy Backend to Zeabur**:
   Since the database is on Zeabur, deploying the backend there too will:
   - Eliminate network issues (same internal network)
   - Provide better performance (lower latency)
   - Simplify deployment

## Quick Test Script
Save as `test_connection.py`:
```python
import pymysql
import sys

try:
    conn = pymysql.connect(
        host='47.84.57.156',
        port=31910,
        user='root',
        password='N81P265Ru7ODZkp0VQz943GMibgExJqK',
        database='zeabur',
        connect_timeout=30
    )
    print("✅ Connection successful!")
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    print(f"MySQL version: {cursor.fetchone()[0]}")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)
```

Run: `python test_connection.py`
