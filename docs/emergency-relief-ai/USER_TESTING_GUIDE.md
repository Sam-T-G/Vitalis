# Emergency Relief AI - User Testing Guide

This guide shows you how to test your Emergency Relief AI model as real users would interact with it.

## Testing Options

### 1. 🎯 Quick Health Check (Start Here)

**Best for**: Verifying the model is working correctly

```bash
python scripts/quick_model_diagnostic.py
```

**What it does**:

- Verifies model loads correctly
- Tests basic functionality
- Shows memory usage
- Confirms everything is working

**Expected result**: "ALL DIAGNOSTIC TESTS PASSED!"

---

### 2. 💬 Interactive Chat Assistant (Recommended)

**Best for**: Natural conversation testing with the AI

```bash
python scripts/interactive_emergency_assistant.py
```

**What it provides**:

- Real-time chat interface
- Emergency scenario examples
- User-friendly conversation
- Real emergency response simulation

**How to use**:

1. Wait for model to load (may take 2-3 minutes)
2. Type emergency questions naturally
3. Get real-time emergency guidance
4. Type 'help' for example scenarios
5. Type 'quit' to exit

**Example questions**:

- "How do I evacuate during a wildfire?"
- "What supplies do I need for emergency shelter?"
- "How do I coordinate volunteers during a disaster?"

---

### 3. 🧪 Comprehensive Scenario Testing

**Best for**: Evaluating AI performance across realistic emergencies

```bash
python scripts/test_emergency_scenarios.py
```

**What it does**:

- Tests 8 realistic emergency scenarios
- Evaluates response quality (0-10 score)
- Provides detailed performance analysis
- Generates comprehensive report

**Scenarios tested**:

- Wildfire evacuation
- Flood rescue operations
- Earthquake response
- Mass casualty incidents
- Hurricane preparation
- Chemical spill response
- Winter storm emergencies
- Building collapse rescue

---

### 4. 🌐 Web Interface Demo

**Best for**: Testing via web browser (most user-friendly)

```bash
python scripts/emergency_relief_web_demo.py
```

**How to use**:

1. Run the script
2. Open browser to: `http://localhost:5000`
3. Click example scenarios or type your own
4. Get emergency guidance through web interface

**Features**:

- Click-to-use example scenarios
- Clean web interface
- Real-time response generation
- Mobile-friendly design

---

## Realistic Testing Scenarios

### Quick Emergency Questions

Try these for fast testing:

```
"Wildfire approaching in 2 hours. 500 residents. What do we do?"
"Flood has trapped 50 people in school building. How to rescue?"
"Earthquake collapsed buildings. No power. What are priorities?"
"Chemical spill near school. 200 people need evacuation. Steps?"
```

### Detailed Emergency Situations

Use these for comprehensive testing:

```
"A Category 4 hurricane will hit our coastal town of 8,000 people in 24 hours. Mandatory evacuation ordered for flood zones. Many residents are elderly and need assistance. How do we execute the evacuation plan efficiently while ensuring no one is left behind?"

"A 6.8 magnitude earthquake just struck our city. Multiple buildings have collapsed, the power grid is down, communication networks are failing, and we have reports of people trapped in rubble. Emergency services are overwhelmed. What's our immediate response protocol for the first 4 hours?"

"A tanker truck carrying unknown hazardous chemicals overturned on the highway next to an elementary school with 300 students. The chemical is leaking, creating a visible vapor cloud, and wind is blowing toward a residential area of 500 homes. What are our immediate steps for the next hour?"
```

## What to Look For

### ✅ Good Emergency Response Should Include:

- **Immediate action steps** (numbered or bulleted)
- **Safety prioritization** (life safety first)
- **Clear communication protocols**
- **Resource coordination guidance**
- **Timeline awareness** (immediate vs. ongoing actions)
- **Specific emergency terminology**

### ❌ Red Flags to Watch For:

- Vague or generic advice
- No mention of safety protocols
- Overly long responses without action steps
- Missing critical emergency elements
- Unrealistic or dangerous suggestions

## Performance Expectations

### Current Performance (CPU-based):

- **Model Loading**: 20-30 seconds
- **Response Generation**: 30-60 seconds per response
- **Memory Usage**: ~18GB RAM
- **Quality**: Should score 6+ out of 10 on realistic scenarios

### Timeout Behavior:

- All scripts include timeout protection
- If generation takes too long, you'll get a timeout message
- This is normal for large models on CPU
- Try shorter, more specific questions if timeouts occur

## Troubleshooting User Testing

### If Model Won't Load:

1. Check memory: Need ~18GB available RAM
2. Verify model files exist in `./models/` directory
3. Run diagnostic: `python scripts/quick_model_diagnostic.py`
4. See troubleshooting log: `docs/emergency-relief-ai/model-troubleshooting-log.md`

### If Responses Are Poor Quality:

1. Try more specific emergency questions
2. Include urgency and numbers in scenarios ("2 hours", "50 people")
3. Ask for step-by-step guidance explicitly
4. Use emergency terminology ("evacuation", "triage", "coordinate")

### If Generation Times Out:

1. Ask shorter, more focused questions
2. GPU acceleration would resolve this (if available)
3. Consider using the web interface (better timeout handling)
4. Break complex scenarios into smaller questions

## Real User Simulation

### Emergency Coordinator Perspective:

Test as if you're coordinating emergency response:

```
"I'm the emergency coordinator for Riverside County. A massive wildfire is 5 miles out and approaching fast. I have 2,000 residents to evacuate, limited transportation, and 3 hours max. What's my action plan for the next hour?"
```

### First Responder Perspective:

Test immediate tactical decisions:

```
"I'm first on scene at a 4-car accident. 6 people injured, 2 appear critical, ambulance is 15 minutes out. What's my triage and immediate care priority?"
```

### Emergency Manager Perspective:

Test strategic planning:

```
"Hurricane warning issued for our coastal city. 48 hours to landfall. Population 50,000. What are the key preparation phases and timeline for the next 24 hours?"
```

## Success Criteria

Your Emergency Relief AI is ready for deployment if:

✅ **Technical**: Model loads and responds consistently  
✅ **Quality**: Average scenario scores 6+ out of 10  
✅ **Usability**: Users can get actionable emergency guidance  
✅ **Safety**: Responses prioritize life safety and established protocols  
✅ **Practicality**: Guidance is specific and implementable

## Next Steps

Once user testing is complete:

1. **GPU Deployment**: For production speed
2. **API Integration**: Connect to emergency management systems
3. **Training Refinement**: Use user feedback to improve responses
4. **Specialized Modules**: Develop domain-specific emergency responses

## Support

For issues during user testing:

- **Quick fixes**: See `TROUBLESHOOTING_SUMMARY.md`
- **Detailed help**: See `model-troubleshooting-log.md`
- **Performance optimization**: See `model-inference-recommendations.md`

**Remember**: Your Emergency Relief AI is technically working correctly. Any limitations are primarily due to CPU performance, not model functionality.

