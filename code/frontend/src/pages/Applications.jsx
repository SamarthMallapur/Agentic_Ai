import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Trash2 } from 'lucide-react'
import { api } from '../api'
import { Alert, Card, Loading, Page, useLoad } from '../ui'

const EMPTY = { company: '', role: '', job_description: '', status: 'SAVED' }

export default function Applications({ statuses }) {
  const { data: apps, error, loading, reload } = useLoad('/applications')
  const [form, setForm] = useState(EMPTY)
  const [problem, setProblem] = useState('')

  const run = async (action) => {
    setProblem('')
    try { await action(); await reload(); return true } catch (e) { setProblem(e.message); return false }
  }
  const add = async (e) => {
    e.preventDefault()
    if (await run(() => api.post('/applications', form))) setForm(EMPTY)
  }
  const field = (key) => ({ value: form[key], onChange: (e) => setForm({ ...form, [key]: e.target.value }) })

  return (
    <Page title="Applications" intro="Track every application. Paste the job description so the agents can use it.">
      <Card title="Add an application">
        <form onSubmit={add} className="form-grid">
          <label>Company<input required {...field('company')} /></label>
          <label>Role<input required {...field('role')} /></label>
          <label className="wide">Job description<textarea rows="4" {...field('job_description')} /></label>
          <div className="wide"><button className="primary">Add application</button></div>
        </form>
      </Card>
      <Alert kind="error">{problem || error}</Alert>
      <Card title="Your applications">
        {loading && !apps ? <Loading /> : apps?.length === 0 ? <p className="muted">No applications yet. Add your first one above.</p> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Company and role</th><th>Status</th><th>Applied</th><th>Follow up</th><th>Resume score</th><th><span className="sr">Actions</span></th></tr></thead>
              <tbody>
                {apps?.map((a) => (
                  <tr key={a.id}>
                    <td><strong>{a.company}</strong><br /><span className="muted small">{a.role}</span></td>
                    <td><select aria-label={`Status for ${a.company}`} value={a.status} onChange={(e) => run(() => api.patch(`/applications/${a.id}`, { status: e.target.value }))}>{statuses.map((s) => <option key={s}>{s}</option>)}</select></td>
                    <td>{a.applied_on || '-'}</td>
                    <td><input aria-label={`Follow-up date for ${a.company}`} type="date" value={a.follow_up_on || ''} onChange={(e) => run(() => api.patch(`/applications/${a.id}`, { follow_up_on: e.target.value || null }))} /></td>
                    <td>{a.resume_score != null ? `${a.resume_score}/100` : '-'}</td>
                    <td><div className="row-actions"><Link to={`/review?app=${a.id}`}>Review</Link>
                      <button className="icon" aria-label={`Delete ${a.company}`} title="Delete" onClick={() => window.confirm(`Delete ${a.company}?`) && run(() => api.remove(`/applications/${a.id}`))}><Trash2 size={16} /></button></div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </Page>
  )
}
