import { useEffect, useRef, useState } from 'react'
import { Mic, MicOff, Play, Square } from 'lucide-react'
import { api } from '../api'
import { Alert, Bar, Card, Confidence, Page, Tag, toast, useLoad } from '../ui'

const LIMIT = 120
const Speech = window.SpeechRecognition || window.webkitSpeechRecognition

function Delivery({ data }) {
  const items = [['Words', data.words], ['Fillers', data.filler_count], ['Avg sentence', `${data.average_sentence_words} words`]]
  if (data.words_per_minute) items.splice(1, 0, ['Pace', `${data.words_per_minute} wpm`])
  return (
    <>
      <h3>Delivery</h3>
      <div className="delivery">{items.map(([label, value]) => <div key={label}><b>{value}</b><span>{label}</span></div>)}</div>
      {data.tips.length > 0 && <p className="small"><strong>Delivery tip:</strong> {data.tips.join(' ')}</p>}
    </>
  )
}

function Question({ q, applicationId }) {
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [problem, setProblem] = useState('')
  const [left, setLeft] = useState(LIMIT)
  const [running, setRunning] = useState(false)
  const [listening, setListening] = useState(false)
  const recognizer = useRef(null), spokenStart = useRef(null), spokenSeconds = useRef(0)

  useEffect(() => {
    if (!running) return undefined
    const id = setInterval(() => setLeft((value) => { if (value <= 1) { setRunning(false); toast('Time is up. Finish your last point.'); return 0 } return value - 1 }), 1000)
    return () => clearInterval(id)
  }, [running])
  useEffect(() => () => recognizer.current?.stop(), [])

  const stopListening = () => {
    recognizer.current?.stop(); recognizer.current = null
    if (spokenStart.current) spokenSeconds.current += (Date.now() - spokenStart.current) / 1000
    spokenStart.current = null; setListening(false)
  }
  const listen = () => {
    if (listening) return stopListening()
    const speech = new Speech()
    speech.lang = 'en-IN'; speech.continuous = true; speech.interimResults = false
    speech.onresult = (event) => {
      const heard = Array.from(event.results).slice(event.resultIndex).filter((r) => r.isFinal).map((r) => r[0].transcript).join(' ').trim()
      if (heard) setAnswer((text) => `${text}${text ? ' ' : ''}${heard}`)
    }
    speech.onerror = (event) => { setProblem(event.error === 'not-allowed' ? 'Microphone access was blocked.' : 'Voice input stopped. You can type instead.'); stopListening() }
    speech.onend = () => { if (recognizer.current === speech) stopListening() }
    recognizer.current = speech; spokenStart.current = Date.now(); speech.start(); setListening(true); setRunning(true)
    return undefined
  }
  const submit = async () => {
    stopListening(); setRunning(false); setBusy(true); setProblem('')
    try { setResult(await api.post('/interview/answer', { question: q, answer, application_id: applicationId, spoken_seconds: spokenSeconds.current > 0 ? spokenSeconds.current : null })) }
    catch (e) { setProblem(e.message) } finally { setBusy(false) }
  }
  const time = `${Math.floor(left / 60)}:${String(left % 60).padStart(2, '0')}`
  return (
    <Card>
      <div className="card-top"><Tag>{q.category}</Tag><span className={`timer ${left <= 20 ? 'low' : ''}`} aria-label={`${left} seconds left`}>{time}</span></div>
      <h3 className="question">{q.question}</h3>
      <details><summary>What a strong answer covers</summary><ul>{q.answer_points.map((p) => <li key={p}>{p}</li>)}</ul></details>
      <label>Your answer<textarea rows="4" value={answer} onChange={(e) => setAnswer(e.target.value)} /></label>
      <div className="answer-actions">
        <button onClick={() => setRunning(!running)}>{running ? <Square size={14} /> : <Play size={14} />} {running ? 'Pause timer' : 'Start timer'}</button>
        {Speech && <button className={listening ? 'danger-live listening' : ''} onClick={listen}>{listening ? <MicOff size={15} /> : <Mic size={15} />} {listening ? 'Stop speaking' : 'Speak answer'}</button>}
        <button className="primary" disabled={busy} onClick={submit}>{busy ? 'Checking...' : 'Get feedback'}</button>
      </div>
      {Speech && <p className="muted small">Voice uses your browser's speech service, which may process audio online.</p>}
      <Alert kind="error">{problem}</Alert>
      {result && (
        <div className="feedback">
          <strong>{result.score}/10</strong> <Confidence level={result.confidence} /> <span className="muted small">{result.method}</span>
          {['relevance', 'structure', 'specificity', 'clarity'].map((k) => <Bar key={k} label={k[0].toUpperCase() + k.slice(1)} value={result[k]} max={10} text={`${result[k]}/10`} />)}
          <Delivery data={result.delivery} />
          {result.strengths.length > 0 && <p><strong>Strengths:</strong> {result.strengths.join(' ')}</p>}
          {result.improvements.length > 0 && <p><strong>Improve:</strong> {result.improvements.join(' ')}</p>}
          <p className="muted small">{result.note}</p>
        </div>
      )}
    </Card>
  )
}

export default function Interview() {
  const { data: apps } = useLoad('/applications')
  const [selected, setSelected] = useState('')
  const [set, setSet] = useState(null)
  const [busy, setBusy] = useState(false)
  const [problem, setProblem] = useState('')
  const usable = apps?.filter((a) => a.job_description) || []
  useEffect(() => { if (!selected && usable[0]) setSelected(String(usable[0].id)) }, [apps]) // eslint-disable-line
  const app = usable.find((a) => String(a.id) === selected)
  const generate = async () => {
    setBusy(true); setProblem(''); setSet(null)
    try { setSet(await api.post('/interview/questions', { jd: app.job_description, role: app.role, application_id: app.id })) }
    catch (e) { setProblem(e.message) } finally { setBusy(false) }
  }
  return (
    <Page title="Interview Coach" intro="Practise under time pressure. Type or speak, then review content and delivery.">
      <Card>
        {apps && !usable.length ? <p className="muted">Add an application with a job description first.</p> : (
          <div className="inline-form">
            <label>Application<select value={selected} onChange={(e) => setSelected(e.target.value)}>{usable.map((a) => <option key={a.id} value={a.id}>{a.company}: {a.role}</option>)}</select></label>
            <button className="primary" disabled={busy || !app} onClick={generate}>{busy ? 'Preparing...' : 'Create questions'}</button>
          </div>
        )}
        <Alert kind="error">{problem}</Alert>
      </Card>
      {set && <><p className="muted small">Source: {set.source}{set.gaps.length ? `. Gaps used: ${set.gaps.join(', ')}` : ''}</p>{set.questions.map((q) => <Question key={q.question} q={q} applicationId={set.application_id} />)}</>}
    </Page>
  )
}
