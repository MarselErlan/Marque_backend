# 📱 Enable Real SMS Sending - Quick Guide

## ✅ What I Fixed

I've updated your `auth_service.py` to **actually send SMS via Twilio** instead of just logging the code!

### Changes Made:

1. ✅ Added Twilio Client initialization
2. ✅ Created `_send_sms_via_twilio()` method
3. ✅ Integrated SMS sending into verification code flow
4. ✅ Added proper error handling and logging

---

## 🚨 ACTION REQUIRED: Set Twilio Phone Number

You need to add one more environment variable to Railway:

### Step 1: Get Your Twilio Phone Number

1. Go to [Twilio Console](https://console.twilio.com/)
2. Click on **Phone Numbers** → **Manage** → **Active numbers**
3. Copy your Twilio phone number (format: `+1XXXXXXXXXX`)

### Step 2: Add to Railway

**Option A: Via Railway Dashboard**

1. Go to [Railway Dashboard](https://railway.app/)
2. Select your **marque_backend** project
3. Click on **Variables** tab
4. Add new variable:
   - **Key:** `TWILIO_PHONE_NUMBER`
   - **Value:** Your Twilio phone number (e.g., `+13128059851`)
5. Click **Save**

**Option B: Via Railway CLI**

```bash
railway variables --set TWILIO_PHONE_NUMBER="+1XXXXXXXXXX"
```

Replace `+1XXXXXXXXXX` with your actual Twilio phone number.

---

## 📤 Deploy the Changes

### Push to GitHub (Automatic Deployment)

```bash
# Stage changes
git add src/app_01/services/auth_service.py

# Commit
git commit -m "feat: enable real SMS sending via Twilio"

# Push
git push origin main
```

Railway will automatically deploy and restart your service!

---

## 🧪 Test SMS Sending

After deploying, test with a real phone number:

```bash
curl -X POST "https://marquebackend-production.up.railway.app/api/v1/auth/send-verification" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1YOUR_PHONE_NUMBER"}'
```

Replace `+1YOUR_PHONE_NUMBER` with your actual phone number.

**You should receive an SMS with your verification code!** 📱

---

## 🔍 Verify It's Working

### Check Railway Logs

```bash
railway logs --follow
```

Look for:

- ✅ `✅ Twilio SMS sent successfully - SID: SMxxxxxxxx`
- ✅ `✅ SMS sent to +1 (XXX) XXX-XXXX via Twilio`

If you see:

- ⚠️ `Twilio not configured - running in demo mode`
  → Make sure `TWILIO_PHONE_NUMBER` is set
- ❌ `Twilio SMS failed: ...`
  → Check error message and Twilio console

---

## 📝 Current Environment Variables

Your Railway project needs these Twilio variables:

| Variable                    | Status         | Notes                |
| --------------------------- | -------------- | -------------------- |
| `TWILIO_ACCOUNT_SID`        | ✅ Set         | Account identifier   |
| `TWILIO_AUTH_TOKEN`         | ✅ Set         | Authentication token |
| `TWILIO_VERIFY_SERVICE_SID` | ✅ Set         | Verify service       |
| `TWILIO_PHONE_NUMBER`       | ❌ **MISSING** | **SET THIS NOW**     |

---

## 🎯 How It Works Now

### Before (Demo Mode):

```python
# Just logged the code
logger.info(f"SMS sent to {phone}: Your verification code is {code}")
```

### After (Real SMS):

```python
# Actually sends SMS via Twilio
message = twilio_client.messages.create(
    body=f"Your Marque verification code is: {code}",
    from_=TWILIO_PHONE_NUMBER,  # Your Twilio number
    to=phone  # User's phone
)
logger.info(f"✅ Twilio SMS sent successfully - SID: {message.sid}")
```

---

## 🔒 SMS Message Format

Users will receive:

```
Your Marque verification code is: 123456
```

You can customize this message in `auth_service.py` line 466.

---

## 💰 Twilio Costs

- **Trial Account:** Limited to verified phone numbers
- **Paid Account:** ~$0.0075 per SMS (varies by country)

Check [Twilio Pricing](https://www.twilio.com/sms/pricing) for your region.

---

## 🚨 Troubleshooting

### "Twilio not configured - running in demo mode"

**Cause:** `TWILIO_PHONE_NUMBER` not set or Twilio client failed to initialize.

**Fix:**

1. Set `TWILIO_PHONE_NUMBER` in Railway
2. Restart the service
3. Check logs for initialization errors

### "The 'From' number +1XXXXXXXXXX is not a valid phone number"

**Cause:** Invalid or unverified Twilio phone number.

**Fix:**

1. Verify your Twilio phone number is active
2. Check format: must include country code (`+1XXX...`)
3. Ensure number is not expired

### "Permission Denied" or "Cannot send to this number"

**Cause:** Trial account restrictions.

**Fix:**

1. Verify recipient phone number in Twilio console
2. Or upgrade to paid Twilio account

---

## ✅ Success Checklist

- [ ] Get Twilio phone number from console
- [ ] Add `TWILIO_PHONE_NUMBER` to Railway variables
- [ ] Push updated code to GitHub
- [ ] Wait for Railway deployment (2-3 min)
- [ ] Test with `curl` command
- [ ] **Receive real SMS on your phone!** 🎉

---

## 📞 Next Steps

1. **Set `TWILIO_PHONE_NUMBER`** in Railway (most important!)
2. **Push code to GitHub** to deploy changes
3. **Test with your phone number**
4. **Verify you receive SMS**
5. **Complete the full auth flow** (send → verify → get token)

---

**Need Help?**

- Check Railway logs: `railway logs`
- Check Twilio logs: [Twilio Console → Monitor → Logs](https://console.twilio.com/monitor/logs/sms)

---

**Ready to send real SMS!** 📱✨
