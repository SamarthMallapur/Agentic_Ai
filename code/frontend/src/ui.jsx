import { useEffect, useState } from 'react'
import { api } from './api'

export function useLoad(path) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const reload = () => {
    setLoading(true)
    return api.get(path).then((value) => { setData(value); setError('') })
      .catch((e) => setError(e.message)).finally(() => setLoading(false))
  }
  useEffect(() => { reload() }, [path]) // eslint-disable-line
  return { data, setData, error, loading, reload }
}

export const Page = ({ title, intro, action, children }) => (
  <>
    <header className="page-head">
      <div><h1>{title}</h1>{intro && <p className="muted">{intro}</p>}</div>
      {action}
    </header>
    {children}
  </>
)

export const Card = ({ title, note, children, className = '' }) => (
  <section className={`card ${className}`}>
    {title && <h2>{title}</h2>}
    {note && <p className="muted small">{note}</p>}
    {children}
  </section>
)

export const Alert = ({ kind = 'info', children }) => children ? <div className={`alert ${kind}`} role="status">{children}</div> : null
export const Loading = ({ text = 'Loading...' }) => <p className="muted">{text}</p>
export const Confidence = ({ level }) => <span className={`tag conf-${(level || '').toLowerCase()}`}>{level} confidence</span>
export const Tag = ({ kind = '', children }) => <span className={`tag ${kind}`}>{children}</span>

export function Bar({ label, value, max = 100, text, muted }) {
  return (
    <div className="bar-row" title={`${label}: ${text ?? value}`}>
      <span className="bar-label">{label}</span>
      <span className="bar-track"><span className={`bar-fill ${muted ? 'is-muted' : ''}`} style={{ width: `${Math.min(100, (100 * value) / max)}%` }} /></span>
      <span className="bar-value">{text ?? value}</span>
    </div>
  )
}

export function DataNotice({ dataset }) {
  if (!dataset?.note) return null
  return <Alert kind="warn"><strong>Data notice:</strong> {dataset.note}</Alert>
}

export function Citations({ claim }) {
  const [posting, setPosting] = useState(null)
  return (
    <div className="citations">
      <span className="muted small">Sources:</span>
      {claim.citations.map((c) => (
        <button key={c.posting_id} className="link" onClick={() => api.get(`/postings/${c.posting_id}`).then(setPosting)}>
          Posting #{c.posting_id}
        </button>
      ))}
      {posting && (
        <div className="source-box">
          <strong>{posting.title}</strong> · {posting.company || 'Company not listed'} · {posting.posted_on || 'No date'}
          <div className="muted small">{posting.source}, row {posting.source_row}</div>
          <p>{posting.description}</p>
          <button className="link" onClick={() => setPosting(null)}>Close</button>
        </div>
      )}
    </div>
  )
}
