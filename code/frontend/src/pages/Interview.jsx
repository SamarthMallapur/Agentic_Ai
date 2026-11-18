import { useEffect, useState } from 'react'
import { api } from '../api'
import { Alert, Bar, Card, Confidence, Page, Tag, useLoad } from '../ui'

function Question({ q, applicationId }) {
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [problem, setProblem] = useState('')
  const submit = async () => {
    setBusy(true); setProblem('')
    try { setResult(await api.post('/interview/answer', { question: q, answer, application_id: applicationId })) }
    catch (e) { setProblem(e.message) } finally { setBusy(false) }
  }
  return (
    <Card>
      <Tag>{q.category}</Tag>
      <h3 className="question">{q.question}</h3>
      <details><summary>What a strong answer covers</summary><ul>{q.answer_points.map((p) => <li key={p}>{p}</li>)}</ul></details>
      <label>Your answer<textarea rows="4" value={answer} onChange={(e) => setAnswer(e.target.value)} /></label>
      <button disabled={busy} onClick={submit}>{busy ? 'Checking...' : 'Get feedback'}</button>
      <Alert kind="error">{problem}</Alert>
      {result && (
        <div className="feedback">
          <strong>{result.score}/10</strong> <Confidence level={result.confidence} /> <span className="muted small">{result.method}</span>
          {['relevance', 'structure', 'specificity', 'clarity'].map((k) => <Bar key={k} label={k[0].toUpperCase() + k.slice(1)} value={result[k]} max={10} text={`${result[k]}/10`} />)}
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
    <Page title="Interview Coach" intro="Practise five questions built from the job and your skill gaps.">
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
