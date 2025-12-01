# To See the Login Screen

You're currently logged in with a saved session. To see the login screen:

## Option 1: Type /logout command
In the terminal, type:
```
/logout
```

## Option 2: Clear localStorage manually
Open browser console (F12) and run:
```javascript
localStorage.removeItem('jwt_token');
location.reload();
```

## Option 3: Clear browser data
- Chrome/Edge: Settings > Privacy > Clear browsing data > Cookies and site data
- Firefox: Settings > Privacy > Clear Data > Cookies

Then refresh the page!

---

## What You'll See After Logout:

1. **Clean login screen:**
   ```
   GATEKEEPER
   
   > USERNAME:
     (Type "register" if you need to create an account)
   ```

2. **Type your username** (or "register" to create new account)

3. **Type your password**

4. **After successful auth:**
   - Shows "✓ ACCESS GRANTED"
   - Clears screen
   - Shows beautiful dial-up sequence with:
     - Modem initialization
     - Dialing sounds ♪♫♪
     - Connection progress dots
     - GATEKEEPER ASCII art
     - "SECURE CONNECTION ESTABLISHED"

5. **Then connects to chat!**
