# Support Bot User Guide

## Welcome

Welcome to the Obsidian BBS Support Bot! This guide will help you understand how the Support Bot works, when it activates, and how to use it effectively.

## What is the Support Bot?

The Support Bot is an empathetic AI assistant that provides emotional support when you're going through a difficult time. It's designed to:

- **Listen without judgment** to what you're experiencing
- **Ask thoughtful questions** to understand your situation
- **Validate your feelings** and let you know they're okay
- **Suggest coping strategies** that might help
- **Connect you with professional resources** if you're in crisis

### What the Support Bot is NOT

❌ **Not a therapist or counselor** - It can't provide professional therapy  
❌ **Not a diagnostic tool** - It won't diagnose mental health conditions  
❌ **Not an emergency service** - For emergencies, call emergency services or crisis hotlines  
❌ **Not a replacement for professional help** - It's a supportive listener, not a substitute for therapy

## How Does It Work?

### Automatic Activation

The Support Bot activates automatically when the system detects that you might be experiencing distress. This happens when:

1. **You send a message** expressing negative emotions
2. **The system analyzes** your message for emotional content
3. **If high-intensity negative sentiment is detected**, the Support Bot activates
4. **A private support room is created** just for you
5. **You're automatically joined** to the support room
6. **The Support Bot greets you** with an empathetic message

### What Triggers Support?

The system looks for expressions of:

- **Sadness**: Feeling down, depressed, lonely, hopeless
- **Anger**: Feeling furious, enraged, or intensely frustrated
- **Frustration**: Feeling stuck, annoyed, or fed up
- **Anxiety**: Feeling worried, scared, nervous, or panicked

**Example messages that might trigger support**:
- "I'm feeling really down today"
- "Everything is so overwhelming"
- "I'm so frustrated I can't take it anymore"
- "I'm really anxious about everything"

### What Happens Next?

Once the Support Bot activates:

1. **You'll see a greeting message** like:
   ```
   [SUPPORT] Hi there. I noticed you might be going through a tough time. 
   I'm here to listen without judgment. What's on your mind right now?
   ```

2. **You're in a private support room** - No one else can see your conversation

3. **You can respond** and have a conversation with the bot

4. **The bot will ask questions** to understand your situation better

5. **You can leave anytime** using the `/leave` command

## Using the Support Bot

### Having a Conversation

The Support Bot is designed to be a good listener. Here's what you can expect:

**The bot will**:
- Ask open-ended questions to understand your situation
- Validate your feelings ("That sounds really difficult")
- Express empathy and understanding
- Suggest general coping strategies when appropriate
- Encourage you to share more if you're comfortable

**Example conversation**:
```
You: I'm feeling really overwhelmed with everything

[SUPPORT] That sounds really difficult. It's completely understandable 
to feel overwhelmed when dealing with so much at once. Can you tell me 
more about what's been weighing on you the most?

You: Work has been really stressful and I can't seem to catch a break

[SUPPORT] I hear you. Work stress can be exhausting, especially when 
it feels relentless. Have you been able to take any time for yourself, 
even just small moments to breathe?
```

### Tips for Getting the Most Out of Support

1. **Be honest about how you're feeling** - The bot is here to listen, not judge
2. **Share as much or as little as you're comfortable with** - You're in control
3. **Ask for what you need** - If you want advice, ask. If you just want to vent, say so
4. **Take your time** - There's no rush. Respond when you're ready
5. **Remember it's AI** - The bot is helpful but has limitations

### Leaving the Support Room

You can leave the support room at any time:

```
/leave
```

When you leave:
- You'll return to your previous room
- The support room stays available if you want to return
- Your conversation history is preserved
- You can come back anytime

### Returning to Support

If you want to return to your support room:

```
/join support_<your_username>_<timestamp>
```

Your conversation history will still be there, and the Support Bot will continue from where you left off.

## Crisis Situations

### What Happens in a Crisis?

If the system detects that you're in a crisis situation (expressing thoughts of self-harm, suicide, or experiencing abuse), it will:

1. **Immediately provide crisis hotline information**
2. **NOT engage in conversation** (crisis situations need professional help)
3. **Encourage you to reach out** to the hotlines provided

### Crisis Hotlines

The system provides Indian crisis hotlines based on the situation:

#### For Self-Harm or Suicide:

**AASRA**
- Phone: 91-9820466726
- Available 24/7
- Provides crisis counseling and emotional support

**Vandrevala Foundation**
- Phone: 1860-2662-345
- Available 24/7
- Mental health support and crisis intervention

**Sneha India**
- Phone: 91-44-24640050
- Available 24/7
- Suicide prevention counseling

#### For Abuse:

**Women's Helpline**
- Phone: 1091
- Available 24/7
- For women experiencing domestic violence or abuse

**Childline India**
- Phone: 1098
- Available 24/7
- For children experiencing abuse or neglect

### Why No Conversation During Crisis?

Crisis situations require professional intervention. The Support Bot:
- Is not trained in crisis counseling
- Cannot assess immediate danger
- Cannot provide emergency intervention
- Cannot replace professional crisis services

**The bot will provide hotlines and encourage you to call them immediately.**

## Privacy and Security

### Your Privacy is Protected

- **Your conversations are private** - Only you can see them
- **Messages are not stored in plaintext** - They're hashed for privacy
- **No one else can join your support room** - It's private to you
- **Your data is not shared** - We never share your information with third parties

### What We Collect

We collect minimal data to provide support:
- When support was activated (timestamp)
- What emotion was detected (sadness, anger, etc.)
- How intense the emotion was (0.0 to 1.0 scale)
- Hashed version of messages (not the actual text)

### What We DON'T Collect

- Full message transcripts
- Personal identifying information
- Medical history or diagnoses
- Location data
- Device information

### Your Rights

You have the right to:
- Leave the support room at any time
- Request deletion of your data
- Ask what data is stored about you
- Opt out of support (by leaving the room)

## Frequently Asked Questions

### Q: Will other users see my support conversation?

**A:** No. Support rooms are completely private. Only you and the Support Bot can see the conversation.

### Q: Can I turn off the Support Bot?

**A:** The Support Bot activates automatically when negative sentiment is detected, but you can immediately leave the support room using `/leave`. You're never forced to engage with it.

### Q: What if I don't want support right now?

**A:** Just use `/leave` to exit the support room and return to normal chat. The support room will be preserved if you change your mind later.

### Q: Will my messages be shared with anyone?

**A:** No. Your messages are hashed (not stored in readable form) and never shared with third parties. Your privacy is protected.

### Q: Can the Support Bot diagnose me?

**A:** No. The Support Bot is not a diagnostic tool and will never diagnose mental health conditions. It's a supportive listener, not a medical professional.

### Q: What if I'm in immediate danger?

**A:** If you're in immediate danger, call emergency services (112 in India) or one of the crisis hotlines provided by the system. The Support Bot will provide these numbers if it detects a crisis.

### Q: How does the bot know what to say?

**A:** The Support Bot uses AI (Gemini 2.5 Flash) to generate empathetic responses based on your messages and conversation history. It's trained to be supportive and non-judgmental.

### Q: Can I talk about anything?

**A:** Yes, you can share whatever you're comfortable with. The bot is here to listen without judgment. However, for crisis situations, it will provide hotlines instead of conversation.

### Q: Will the bot remember our previous conversations?

**A:** Yes, within the same support session. If you leave and return to the same support room, your conversation history is preserved.

### Q: What if the bot says something unhelpful?

**A:** The bot tries its best, but it's not perfect. If a response isn't helpful, you can:
- Clarify what you need ("I'm not looking for advice, just someone to listen")
- Leave the support room if it's not helping
- Seek professional help if you need more support

### Q: Is this confidential?

**A:** Your conversations are private and hashed before storage. However, this is not the same as professional confidentiality (like with a therapist). For truly confidential support, contact a professional counselor.

## Getting Professional Help

### When to Seek Professional Help

Consider reaching out to a professional if:
- You're experiencing persistent sadness or anxiety
- Your emotions are interfering with daily life
- You're having thoughts of self-harm or suicide
- You're experiencing trauma or abuse
- You want to work through deeper issues
- The Support Bot isn't providing enough support

### How to Find Professional Help

**In India**:

1. **Mental Health Professionals**:
   - Psychiatrists (medical doctors who can prescribe medication)
   - Psychologists (provide therapy and counseling)
   - Counselors (provide support and guidance)

2. **Finding a Therapist**:
   - Ask your primary care doctor for a referral
   - Search online directories (e.g., Practo, 1mg)
   - Contact local mental health clinics
   - Check with your insurance for covered providers

3. **Crisis Services**:
   - AASRA: 91-9820466726
   - Vandrevala Foundation: 1860-2662-345
   - Sneha India: 91-44-24640050

4. **Emergency Services**:
   - Call 112 for immediate emergency assistance
   - Go to the nearest hospital emergency room

### Support Bot vs. Professional Help

| Support Bot | Professional Help |
|-------------|-------------------|
| Available 24/7 instantly | Requires appointment |
| Free | May have costs |
| AI-powered | Human professional |
| General support | Specialized treatment |
| No diagnosis | Can diagnose conditions |
| No prescriptions | Can prescribe medication |
| Limited scope | Comprehensive care |

**The Support Bot is a helpful first step, but professional help is often necessary for ongoing mental health support.**

## Tips for Mental Wellness

While using the Support Bot, here are some general wellness tips:

### Self-Care Basics

1. **Sleep**: Aim for 7-9 hours per night
2. **Exercise**: Even a short walk can help
3. **Nutrition**: Eat regular, balanced meals
4. **Hydration**: Drink plenty of water
5. **Social Connection**: Reach out to friends or family

### Coping Strategies

1. **Deep Breathing**: Slow, deep breaths can calm anxiety
2. **Journaling**: Write down your thoughts and feelings
3. **Mindfulness**: Focus on the present moment
4. **Creative Expression**: Art, music, or writing
5. **Nature**: Spend time outdoors if possible

### When to Use the Support Bot

The Support Bot can be helpful when:
- You need someone to listen
- You're feeling overwhelmed
- You want to process your emotions
- You need a reminder that your feelings are valid
- You're looking for general coping strategies

### When to Seek More Help

Seek professional help when:
- Symptoms persist for more than two weeks
- You're having thoughts of self-harm
- Your emotions are interfering with work or relationships
- You're experiencing trauma or abuse
- You want to work on deeper issues

## Feedback and Support

### Providing Feedback

We want to improve the Support Bot. If you have feedback:
- Contact system administrators
- Share what was helpful or unhelpful
- Suggest improvements
- Report any issues

### Getting Technical Help

If you experience technical issues:
- Contact system administrators
- Describe the problem in detail
- Include any error messages
- Mention what you were doing when the issue occurred

### Reporting Concerns

If you have concerns about:
- Privacy or security
- Inappropriate bot responses
- System behavior
- Safety issues

Please contact system administrators immediately.

## Conclusion

The Support Bot is here to provide a safe, supportive space when you're going through a difficult time. It's not a replacement for professional help, but it can be a helpful resource for emotional support.

**Remember**:
- You're in control - leave anytime
- Your privacy is protected
- The bot is here to listen, not judge
- Professional help is available when you need it
- Your feelings are valid

**If you're in crisis, please reach out to the hotlines provided or call emergency services.**

We hope the Support Bot provides the support you need. Take care of yourself, and remember that it's okay to ask for help.

---

## Quick Reference

### Commands

```
/leave          # Leave support room
/join <room>    # Return to support room
/help           # Show available commands
```

### Crisis Hotlines (India)

```
AASRA: 91-9820466726 (24/7)
Vandrevala Foundation: 1860-2662-345 (24/7)
Sneha India: 91-44-24640050 (24/7)
Women's Helpline: 1091 (24/7)
Childline India: 1098 (24/7)
Emergency Services: 112
```

### Key Points

- ✅ Private and confidential
- ✅ Available 24/7
- ✅ Non-judgmental support
- ✅ Leave anytime
- ❌ Not a therapist
- ❌ Not for emergencies
- ❌ Not a replacement for professional help

---

**Need help right now?** Just send a message expressing how you're feeling, and the Support Bot will be there to listen.
