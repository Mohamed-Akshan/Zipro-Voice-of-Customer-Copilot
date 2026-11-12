
import { useEffect, useState } from 'react'

import {
  ArrowUpRight,
  ChartNoAxesCombined,
  FolderUp,
  Layers,
  MessageCircle,
  MessageSquare,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  X
} from 'lucide-react'

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts'

import { api } from '../api'
import StatCard from '../components/StatCard'


const COLORS = [
  '#376CFB',
  '#14A6A0',
  '#9C80DB',
  '#EAB16D',
  '#5B8BC4'
]


// Upload new customer feedback
function UploadPanel({ onDone, onClose }) {

  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [success, setSuccess] = useState(false)

  async function submit(event) {

    event.preventDefault()

    if (!file || loading) return

    setLoading(true)
    setSuccess(false)
    setMessage('Uploading and indexing customer feedback…')

    try {

      const body = new FormData()
      body.append('file', file)

      const result = await api('/upload', {
        method: 'POST',
        body
      })

      setSuccess(true)

      setMessage(
        `Successfully indexed ${result.records} feedback records ` +
        `and ${result.chunks} chunks.`
      )

      onDone()

    } catch (error) {

      setMessage(error.message)

    } finally {

      setLoading(false)

    }
  }

  return (
    <div
      className="modal-backdrop"
      onClick={() => {
        if (!loading) onClose()
      }}
    >

      <div
        className="modal"
        onClick={event => event.stopPropagation()}
      >

        <div className="modal-head">

          <h2>Import customer feedback</h2>

          <button
            type="button"
            className="icon-btn"
            onClick={onClose}
            disabled={loading}
            aria-label="Close"
          >
            <X size={19} />
          </button>

        </div>

        <p className="muted">
          Upload new customer feedback to update your insights.
          Records become searchable after indexing succeeds.
        </p>

        <form onSubmit={submit}>

          <label className="dropzone">

            <UploadCloud size={29} />

            <strong>
              {file?.name || 'Select a customer feedback file'}
            </strong>

            <span>
              CSV, JSON, DOCX, PDF, XLSX • Max 8 MB
            </span>

            <input
              type="file"
              accept=".csv,.json,.docx,.pdf,.xlsx"
              disabled={loading}
              onChange={event => {
                setFile(event.target.files?.[0] || null)
                setMessage('')
                setSuccess(false)
              }}
            />

          </label>

          {message && (
            <p
              className="upload-message"
              role="status"
              style={{
                color: success ? '#16794b' : undefined
              }}
            >
              {message}
            </p>
          )}

          <button
            type="submit"
            className="primary-button full"
            disabled={!file || loading}
          >
            {loading
              ? 'Processing feedback…'
              : 'Import and index feedback'}
          </button>

          {success && (
            <button
              type="button"
              className="outline-button"
              onClick={onClose}
              style={{
                width: '100%',
                justifyContent: 'center',
                marginTop: 12
              }}
            >
              Done
            </button>
          )}

        </form>

      </div>

    </div>
  )
}


// Customer Intelligence Dashboard
export default function Dashboard({ openCopilot }) {

  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [uploadOpen, setUploadOpen] = useState(false)

  function refresh() {

    setError('')

    api('/dashboard')
      .then(setData)
      .catch(error => setError(error.message))
  }

  useEffect(() => {
    refresh()
  }, [])

  const issues = data?.issues || []
  const sources = data?.sources || []
  const trends = data?.trends || []
  const total = Number(data?.total || 0)

  return (
    <div className="dashboard">

      {/* Scoped styling for the new import position */}
      <style>{`
        .zi-import-card {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 22px;
          flex-wrap: wrap;
          margin: 24px 0 28px;
          padding: 23px 26px;
          background: #f8faff;
          border: 1px solid #e1e9f8;
          border-radius: 16px;
        }

        .zi-import-content {
          display: flex;
          align-items: center;
          gap: 16px;
          flex: 1;
          min-width: 240px;
        }

        .zi-import-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 48px;
          height: 48px;
          flex-shrink: 0;
          background: #e9f0ff;
          color: #376cfb;
          border-radius: 13px;
        }

        .zi-import-text h2 {
          margin: 0 0 5px;
          font-size: 16px;
          font-weight: 700;
          color: #193654;
        }

        .zi-import-text p {
          margin: 0;
          color: #71839a;
          font-size: 12.5px;
          line-height: 1.7;
          max-width: 590px;
        }

        .zi-import-button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 9px;
          border: none;
          padding: 12px 17px;
          border-radius: 10px;
          background: #376cfb;
          color: white;
          font-size: 12.5px;
          font-weight: 650;
          cursor: pointer;
          white-space: nowrap;
          transition: background 0.2s;
        }

        .zi-import-button:hover {
          background: #2857d3;
        }

        @media (max-width: 650px) {
          .zi-import-card {
            padding: 18px;
            gap: 16px;
          }

          .zi-import-button {
            width: 100%;
          }
        }
      `}</style>

      {/* Dashboard heading */}
      <div className="page-heading">

        <div>

          <div className="eyebrow">
            PRODUCT EXPERIENCE INTELLIGENCE
          </div>

          <h1>Customer intelligence</h1>

          <p>
            Understand what riders are experiencing.
            Decide what deserves attention.
          </p>

        </div>

        <button
          className="outline-button"
          onClick={refresh}
        >
          <RefreshCw size={16} />
          Refresh insights
        </button>

      </div>

      {/* API errors */}
      {error && (
        <div className="alert">
          Could not reach the API: {error}.
          Check that FastAPI is running.
        </div>
      )}

      {/* Dashboard KPI cards */}
      <div className="stat-grid">

        <StatCard
          label="Feedback records"
          value={total.toLocaleString()}
          caption="Across all available sources"
          icon={MessageSquare}
        />

        <StatCard
          label="Issue categories"
          value={(data?.issue_count || 0).toLocaleString()}
          caption="Tagged product experience areas"
          icon={Layers}
          variant="violet"
        />

        <StatCard
          label="Top issue mentions"
          value={(issues[0]?.count || 0).toLocaleString()}
          caption={issues[0]?.name || 'Waiting for feedback'}
          icon={ChartNoAxesCombined}
          variant="teal"
        />

        <StatCard
          label="Feedback sources"
          value={sources.length}
          caption="Connected source types"
          icon={FolderUp}
          variant="orange"
        />

      </div>

      {/* NEW POSITION: Upload feedback below the KPI cards */}
      <section className="zi-import-card">

        <div className="zi-import-content">

          <div className="zi-import-icon">
            <UploadCloud size={23} />
          </div>

          <div className="zi-import-text">

            <h2>Import customer feedback</h2>

            <p>
              Add new reviews, support tickets, surveys,
              interviews or feature requests.
              Zipro will update its customer intelligence
              after successful indexing.
            </p>

          </div>

        </div>

        <button
          className="zi-import-button"
          onClick={() => setUploadOpen(true)}
        >
          <UploadCloud size={17} />
          Import feedback
          <ArrowUpRight size={16} />
        </button>

      </section>

      {/* Existing dashboard charts and insights */}
      <div className="dashboard-grid">

        {/* Feedback volume chart */}
        <section className="panel trend-panel">

          <div className="panel-title">

            <div>
              <h2>Feedback volume</h2>
              <p>Monthly records from the indexed dataset</p>
            </div>

            <div className="panel-tag">
              Monthly
            </div>

          </div>

          <div className="chart-wrap">

            <ResponsiveContainer width="100%" height="100%">

              <LineChart
                data={trends}
                margin={{
                  top: 12,
                  left: -22,
                  right: 16,
                  bottom: 0
                }}
              >

                <CartesianGrid
                  stroke="#edf1f6"
                  vertical={false}
                />

                <XAxis
                  dataKey="month"
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fill: '#8A99AD',
                    fontSize: 11
                  }}
                />

                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fill: '#8A99AD',
                    fontSize: 11
                  }}
                />

                <Tooltip
                  contentStyle={{
                    borderRadius: 12,
                    border: '1px solid #e8edf3'
                  }}
                />

                <Line
                  type="monotone"
                  dataKey="count"
                  name="Feedback records"
                  stroke="#376CFB"
                  strokeWidth={3}
                  dot={{
                    r: 4,
                    strokeWidth: 2,
                    fill: '#fff'
                  }}
                  activeDot={{ r: 7 }}
                />

              </LineChart>

            </ResponsiveContainer>

          </div>

        </section>

        {/* Feedback sources */}
        <section className="panel source-panel">

          <div className="panel-title">
            <div>
              <h2>Feedback sources</h2>
              <p>Where customers are being heard</p>
            </div>
          </div>

          <div className="source-list">

            {sources.map((row, index) => (

              <div
                className="source-item"
                key={row.name}
              >

                <div className="source-label">

                  <span
                    className="color-dot"
                    style={{
                      background: COLORS[
                        index % COLORS.length
                      ]
                    }}
                  />

                  {row.name.replaceAll('_', ' ')}

                  <strong>
                    {Number(row.count).toLocaleString()}
                  </strong>

                </div>

                <div className="progress">

                  <div
                    style={{
                      width: `${
                        total
                          ? Number(row.count) / total * 100
                          : 0
                      }%`,
                      background: COLORS[
                        index % COLORS.length
                      ]
                    }}
                  />

                </div>

              </div>
            ))}

          </div>

          {!sources.length && (
            <p className="empty">
              No source records indexed yet.
            </p>
          )}

        </section>

        {/* Most reported customer problems */}
        <section className="panel issues-panel">

          <div className="panel-title">

            <div>
              <h2>Most reported issues</h2>
              <p>Distinct feedback records by issue category</p>
            </div>

            <span className="hint">
              Not vector chunk counts
            </span>

          </div>

          <div className="issue-list">

            {issues.slice(0, 7).map((row, index) => (

              <div
                className="issue-row"
                key={row.name}
              >

                <span className="issue-rank">
                  {String(index + 1).padStart(2, '0')}
                </span>

                <div className="issue-main">

                  <strong>{row.name}</strong>

                  <div className="issue-bar">

                    <div
                      style={{
                        width: `${
                          Number(row.count) /
                          Math.max(
                            1,
                            Number(issues[0]?.count)
                          ) * 100
                        }%`
                      }}
                    />

                  </div>

                </div>

                <span className="issue-count">
                  {row.count} mentions
                </span>

              </div>
            ))}

          </div>

          {!issues.length && (
            <p className="empty">
              Index the dataset to populate issue insights.
            </p>
          )}

        </section>

        {/* AI Product Decision Copilot */}
        <section className="panel decision-panel">

          <div className="decision-icon">
            <Sparkles size={24} />
          </div>

          <h2>From feedback to product decisions</h2>

          <p>
            Explore recurring complaints, investigate the
            evidence, and get recommendations with
            verified customer quotations.
          </p>

          <div className="decision-points">

            <span>
              <ShieldCheck size={15} />
              Verifiable citations
            </span>

            <span>
              <MessageCircle size={15} />
              Multi-turn investigations
            </span>

            <span>
              <Layers size={15} />
              Hybrid corrective retrieval
            </span>

          </div>

          <button
            className="primary-button"
            onClick={openCopilot}
          >
            Open AI copilot
            <ArrowUpRight size={17} />
          </button>

        </section>

      </div>

      {/* Upload modal */}
      {uploadOpen && (
        <UploadPanel
          onClose={() => setUploadOpen(false)}
          onDone={refresh}
        />
      )}

    </div>
  )
}
