import { useEffect, useRef, useState } from 'react'
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

export function useCountUp(value, duration = 900) {
  const [shown, setShown] = useState(0)
  const previous = useRef(0)
  useEffect(() => {
    const target = Number(value) || 0
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { setShown(target); previous.current = target; return undefined }
    const start = performance.now(), from = previous.current
    let frame
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration), eased = 1 - (1 - t) ** 3
      setShown(Math.round(from + (target - from) * eased))
      if (t < 1) frame = requestAnimationFrame(tick); else previous.current = target
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [value, duration])
  return shown
}

export const CountUp = ({ value }) => useCountUp(value)

export function Ring({ value, label = 'of 100', size = 150 }) {
  const radius = 62, circumference = 2 * Math.PI * radius
  const [offset, setOffset] = useState(circumference)
  const shown = useCountUp(value, 1100)
  useEffect(() => { const id = requestAnimationFrame(() => setOffset(circumference * (1 - value / 100))); return () => cancelAnimationFrame(id) }, [value, circumference])
  return (
    <div className="ring-wrap" style={{ width: size, height: size }} role="img" aria-label={`${value} ${label}`}>
      <svg width={size} height={size} viewBox="0 0 150 150" aria-hidden="true">
        <defs><linearGradient id="ringGradient"><stop offset="0" stopColor="#55e6c1" /><stop offset="1" stopColor="#7cc7ff" /></linearGradient></defs>
        <circle className="ring-bg" cx="75" cy="75" r={radius} />
        <circle className="ring-value" cx="75" cy="75" r={radius} strokeDasharray={circumference} strokeDashoffset={offset} />
      </svg>
      <div className="ring-label"><span>{shown}</span><small>{label}</small></div>
    </div>
  )
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

export function Card({ title, note, children, className = '' }) {
  const spotlight = (e) => {
    const box = e.currentTarget.getBoundingClientRect()
    e.currentTarget.style.setProperty('--mx', `${e.clientX - box.left}px`)
    e.currentTarget.style.setProperty('--my', `${e.clientY - box.top}px`)
  }
  return (
    <section className={`card ${className}`} onPointerMove={spotlight}>
      {title && <h2>{title}</h2>}
      {note && <p className="muted small">{note}</p>}
      {children}
    </section>
  )
}

export const toast = (message) => window.dispatchEvent(new CustomEvent('app-toast', { detail: message }))

export function Toaster() {
  const [items, setItems] = useState([])
  useEffect(() => {
    const add = (e) => {
      const id = Date.now() + Math.random()
      setItems((list) => [...list, { id, message: e.detail }])
      setTimeout(() => setItems((list) => list.filter((item) => item.id !== id)), 3200)
    }
    window.addEventListener('app-toast', add)
    return () => window.removeEventListener('app-toast', add)
  }, [])
  return <div className="toaster" aria-live="polite">{items.map((item) => <div className="toast" key={item.id}>{item.message}</div>)}</div>
}

export const Alert = ({ kind = 'info', children }) => children ? <div className={`alert ${kind}`} role="status">{children}</div> : null
export const Loading = ({ text = 'Loading' }) => <div className="skeleton" role="status" aria-label={text}><i /><i /><i /></div>
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
