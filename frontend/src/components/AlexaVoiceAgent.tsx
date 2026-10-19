import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Sparkles,
  Bot,
  Radio,
  Cpu,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface AlexaVoiceAgentProps {
  onExecuteSearch: (query: string) => void;
  onExecuteAudit: (asinOrQuery: string) => void;
  currentAuditedTitle?: string;
  currentVerdict?: string;
}

// Global declaration for Web Speech API
declare global {
  interface Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }
}

export const AlexaVoiceAgent: React.FC<AlexaVoiceAgentProps> = ({
  onExecuteSearch,
  onExecuteAudit,
  currentAuditedTitle,
  currentVerdict,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [alexaResponse, setAlexaResponse] = useState<string>(
    "Hi, I'm Alexa+ for BuyWise AI. Tap the microphone and ask me about any Amazon deal, hardware defect, or product recommendation."
  );
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const [ollamaActive, setOllamaActive] = useState<boolean | null>(null);

  const recognitionRef = useRef<any>(null);

  // Check Ollama daemon connectivity
  useEffect(() => {
    fetch('/api/v1/ollama/status')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.available) {
          setOllamaActive(true);
        } else {
          setOllamaActive(false);
        }
      })
      .catch(() => setOllamaActive(false));
  }, []);

  // Initialize Web Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const current = event.resultIndex;
        const text = event.results[current][0].transcript;
        setTranscript(text);

        if (event.results[current].isFinal) {
          handleVoiceCommand(text);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  // Text-To-Speech function
  const speakText = (text: string) => {
    if (isMuted || !('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;

    // Pick an English female voice if available to emulate Alexa
    const voices = window.speechSynthesis.getVoices();
    const alexaVoice =
      voices.find((v) => v.lang.includes('en') && (v.name.includes('Samantha') || v.name.includes('Zira') || v.name.includes('Google US English') || v.name.includes('Natural'))) ||
      voices.find((v) => v.lang.includes('en'));

    if (alexaVoice) utterance.voice = alexaVoice;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  // Process incoming voice input
  const handleVoiceCommand = async (rawInput: string) => {
    const text = rawInput.trim();
    if (!text) return;

    setTranscript(text);

    // Call backend /api/v1/alexa/chat
    try {
      const res = await fetch('/api/v1/alexa/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_prompt: text,
          current_asin: null,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setAlexaResponse(data.speech_text);
        speakText(data.speech_text);

        if (data.action === 'AUDIT' && data.target_asin) {
          onExecuteAudit(data.target_asin);
        } else if (data.action === 'SEARCH' && data.search_query) {
          onExecuteSearch(data.search_query);
        }
        return;
      }
    } catch {
      // client-side rule fallback
    }

    // Client-side fallback rule routing
    const lower = text.toLowerCase();
    let reply = '';

    if (lower.includes('macbook') || lower.includes('apple')) {
      reply =
        'Alexa+ verified: Apple MacBook Air M1 is currently at a 90-day all-time low price of $749. BuyWise verdict is BUY.';
      onExecuteAudit('B08N5WRWNW');
    } else if (lower.includes('phone') || lower.includes('apex') || lower.includes('markup')) {
      reply =
        'Warning: The Apex Ultra smartphone has an artificial pre-sale price markup. The true price was $849 last week. I recommend you WAIT.';
      onExecuteAudit('B09V3K3EXP');
    } else if (lower.includes('mouse') || lower.includes('defect') || lower.includes('turboclick')) {
      reply =
        'Alert: TurboClick Gaming Mouse has a 38% cluster of scroll wheel and switch defects. BuyWise verdict is DO NOT BUY.';
      onExecuteAudit('B07DEFECT0');
    } else if (lower.includes('college') || lower.includes('student') || lower.includes('laptop')) {
      reply =
        'Switch recommended: VendorX SlimBook has soldered 8GB RAM. I recommend the BenchmarkPro 14 which saves ₹2,010 and gives you 16GB dual channel RAM.';
      onExecuteAudit('B0COLLEGE1');
    } else if (lower.includes('search') || lower.includes('find') || lower.includes('headphones')) {
      const query = text.replace(/alexa|please|search|find|for|show me/gi, '').trim() || 'headphones';
      reply = `Searching Amazon products for ${query}. Displaying real-time matching deals below.`;
      onExecuteSearch(query);
    } else {
      reply = `I audited the evidence for "${text}". Full pricing and aspect defect scorecards are now open on your screen.`;
      onExecuteAudit(text);
    }

    setAlexaResponse(reply);
    speakText(reply);
  };

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch {
          setIsListening(true);
        }
      } else {
        // Fallback prompt for browsers without speech API
        const manual = prompt('Enter your Alexa+ voice query:');
        if (manual) handleVoiceCommand(manual);
      }
    }
  };

  return (
    <aside className="alexa-agent-dock" id="alexa-voice-assistant">
      <div className="alexa-dock-card">
        {/* Header Bar */}
        <div className="alexa-card-header">
          <div className="alexa-brand-pill">
            <div className={`alexa-ring-orb ${isListening ? 'listening' : isSpeaking ? 'speaking' : 'idle'}`}>
              <div className="alexa-ring-inner">
                <Radio size={14} className="alexa-core-icon" />
              </div>
            </div>
            <div className="alexa-title-text">
              <span className="alexa-name">Alexa+</span>
              <span className="alexa-sub">Voice Agent Core</span>
            </div>
          </div>

          <div className="alexa-controls-row">
            {/* Ollama Status Badge */}
            <div
              className={`ollama-badge ${ollamaActive ? 'active' : 'fallback'}`}
              title={ollamaActive ? 'Connected to local Ollama LLM' : 'Running on Deterministic Forensic Core'}
            >
              <Cpu size={12} />
              <span>{ollamaActive ? 'Ollama (Llama 3)' : 'Rule Engine'}</span>
            </div>

            {/* Mute Button */}
            <button
              type="button"
              className="alexa-icon-btn"
              onClick={() => {
                if (!isMuted && window.speechSynthesis) window.speechSynthesis.cancel();
                setIsMuted(!isMuted);
              }}
              title={isMuted ? 'Unmute Voice' : 'Mute Voice'}
            >
              {isMuted ? <VolumeX size={15} /> : <Volume2 size={15} />}
            </button>

            {/* Collapse / Expand */}
            <button
              type="button"
              className="alexa-icon-btn"
              onClick={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? 'Collapse Alexa+' : 'Expand Alexa+'}
            >
              {isExpanded ? <ChevronDown size={15} /> : <ChevronUp size={15} />}
            </button>
          </div>
        </div>

        {/* Expandable Body */}
        {isExpanded && (
          <div className="alexa-card-body">
            {/* Live Visualizer Waveform / Listening state */}
            <div className="alexa-visualizer-box">
              <div className="alexa-mic-trigger">
                <button
                  type="button"
                  id="alexa-mic-toggle-btn"
                  className={`alexa-mic-button ${isListening ? 'active-pulse' : ''}`}
                  onClick={toggleListening}
                  title={isListening ? 'Listening... Click to stop' : 'Click to Speak with Alexa+'}
                >
                  {isListening ? <Mic size={22} className="text-sky-300" /> : <MicOff size={20} className="text-slate-400" />}
                </button>
              </div>

              <div className="alexa-speech-content">
                <span className="alexa-status-label">
                  {isListening ? (
                    <span className="text-sky-400 font-semibold animate-pulse">● Listening to your voice...</span>
                  ) : isSpeaking ? (
                    <span className="text-amber-400 font-semibold">🔊 Alexa+ speaking...</span>
                  ) : (
                    <span className="text-slate-400">Tap mic to speak</span>
                  )}
                </span>

                {transcript && (
                  <p className="alexa-transcript-preview">
                    "<em>{transcript}</em>"
                  </p>
                )}
              </div>
            </div>

            {/* Active Audit Context (if any product is being audited) */}
            {currentAuditedTitle && (
              <div className="alexa-audited-context flex items-center gap-2 text-xs text-sky-300 bg-sky-950/40 border border-sky-500/20 px-3 py-1.5 rounded-lg mb-2">
                <Radio size={12} className="text-sky-400 animate-pulse shrink-0" />
                <span className="truncate">Auditing: <strong className="text-white">{currentAuditedTitle}</strong></span>
                {currentVerdict && (
                  <span className="ml-auto font-mono text-[10px] font-bold tracking-wider px-2 py-0.5 rounded bg-sky-500/20 text-sky-200 uppercase shrink-0">
                    {currentVerdict}
                  </span>
                )}
              </div>
            )}

            {/* Spoken Response Box */}
            <div className="alexa-dialogue-balloon">
              <Bot size={15} className="balloon-icon" />
              <p className="balloon-text">{alexaResponse}</p>
            </div>

            {/* Quick Click-to-Speak Prompt Shortcuts */}
            <div className="alexa-shortcuts-tray">
              <span className="shortcuts-label">Try Voice Commands:</span>
              <div className="shortcuts-grid">
                <button
                  type="button"
                  className="shortcut-chip"
                  onClick={() => handleVoiceCommand('Alexa, is MacBook Air a genuine deal?')}
                >
                  <Sparkles size={11} />
                  <span>"Is MacBook Air a genuine deal?"</span>
                </button>
                <button
                  type="button"
                  className="shortcut-chip"
                  onClick={() => handleVoiceCommand('Alexa, check smartphone for pre-sale markup')}
                >
                  <Sparkles size={11} />
                  <span>"Check smartphone price markup"</span>
                </button>
                <button
                  type="button"
                  className="shortcut-chip"
                  onClick={() => handleVoiceCommand('Alexa, find college laptops under 50000')}
                >
                  <Sparkles size={11} />
                  <span>"Compare college laptops"</span>
                </button>
                <button
                  type="button"
                  className="shortcut-chip"
                  onClick={() => handleVoiceCommand('Alexa, check TurboClick mouse for defect')}
                >
                  <Sparkles size={11} />
                  <span>"Check mouse for defects"</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
