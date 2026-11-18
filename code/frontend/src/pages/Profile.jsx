import { useEffect, useState } from 'react'
import { api } from '../api'
import { Alert, Card, Loading, Page, Tag, useLoad } from '../ui'

const list = (text) => text.split(',').map((s) => s.trim()).filter(Boolean)

export default function Profile() {
  const { data, error, loading } = useLoad('/profile')
  const memory = useLoad('/feedback')
  const [form, setForm] = useState(null)
  const [message, setMessage] = useState('')
  const [problem, setProblem] = useState('')

  useEffect(() => {
    if (data) setForm({ ...data, target_roles: data.target_roles.join(', '), skills: data.skills.join(', '), weak_areas: data.weak_areas.join(', ') })
  }, [data])

  if (loading || (!form && !error)) return <Loading />
  if (error) return <Alert kind="error">{error}</Alert>
  const field = (key) => ({ value: form[key], onChange: (e) => { setForm({ ...form, [key]: e.target.value }); setMessage('') } })

  const save = async () => {
    setProblem('')
    try {
      await api.put('/profile', { ...form, target_roles: list(form.target_roles), skills: list(form.skills), weak_areas: list(form.weak_areas) })
      setMessage('Profile saved.')
    } catch (e) { setProblem(e.message) }
  }
  const upload = async (file) => {
    if (!file) return
    setProblem('')
    try { setForm({ ...form, resume_text: (await api.upload(file)).text }); setMessage('Resume loaded. Press Save to keep it.') }
    catch (e) { setProblem(e.message) }
  }

  return (
    <Page title="My Profile" intro="This is the long-term memory every agent reads.">
      <Card>
        <div className="form-grid">
          <label>Name<input {...field('name')} /></label>
          <label>Education<input {...field('education')} /></label>
          <label>Graduation year<input {...field('graduation_year')} /></label>
          <label>Target roles (comma separated)<input {...field('target_roles')} /></label>
          <label className="wide">Skills (comma separated)<input {...field('skills')} /></label>
          <label className="wide">Weak areas (comma separated)<input {...field('weak_areas')} /></label>
          <label className="wide">Upload resume (PDF, DOCX or TXT)<input type="file" accept=".pdf,.docx,.txt" onChange={(e) => upload(e.target.files[0])} /></label>
          <label className="wide">Resume text<textarea rows="12" {...field('resume_text')} /></label>
        </div>
        <button className="primary" onClick={save}>Save profile</button>
        <Alert kind="ok">{message}</Alert><Alert kind="error">{problem}</Alert>
      </Card>
      <Card title="Advice memory" note="Advice you rejected is not repeated. Decisions are made on the Resume Review page.">
        {memory.data?.length ? (
          <ul className="plain">
            {memory.data.map((f) => <li key={f.id}><Tag kind={f.decision === 'accepted' ? 'good' : 'bad'}>{f.decision}</Tag> {f.suggestion}{f.reason && <span className="muted"> Reason: {f.reason}</span>}</li>)}
          </ul>
        ) : <p className="muted">No decisions saved yet.</p>}
      </Card>
    </Page>
  )
}
