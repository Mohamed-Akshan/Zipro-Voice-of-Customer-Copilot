
import { useEffect, useRef, useState } from 'react'

import {
  ArrowUpRight,
  BookOpenCheck,
  CheckCircle2,
  ChevronRight,
  History,
  LoaderCircle,
  MessagesSquare,
  Plus,
  Send,
  ShieldCheck,
  Sparkles,
  X
} from 'lucide-react'

import { api, newThreadId } from '../api'


const SUGGESTIONS = [
  'What are the biggest customer complaints?',
  'Which customer issue should Zipro prioritize?',
  'Why are customers unhappy with driver cancellations?',
  'What product improvements would you recommend?'
]


// Display natural, evidence-backed product analysis
function VerifiedAnswer({ answer, onSource }) {

  if (!answer) return null

  if (answer.status !== 'evidence_found') {
    return (
      <div className="zi-answer">
        <p>
          {answer.message || 'Not enough verified evidence.'}
        </p>
      </div>
    )
  }

  const proposals = answer.proposals || []

  return (
    <article className="zi-answer">

      <div className="zi-top">
        <span className="zi-brand">
          <Sparkles size={15} />
          ZIPRO INTELLIGENCE
        </span>

        <span className="zi-verified">
          <ShieldCheck size={14} />
          Evidence checked
        </span>
      </div>

      {/* Show SQL-only answers directly */}
      {proposals.length === 0 ? (
        <p className="zi-intro">
          {answer.summary}
        </p>
      ) : (
        <>
          {/* Main finding */}
          <h2 className="zi-main-title">
            {proposals.length === 1
              ? proposals[0].issue
              : 'Customer intelligence findings'}
          </h2>

          {proposals.length === 1 ? (
            <p className="zi-intro">
              {proposals[0].finding}
            </p>
          ) : (
            <p className="zi-intro">
              {answer.summary}
            </p>
          )}

          {proposals.map((item, index) => (

            <section
              className="zi-proposal"
              key={`${item.issue}-${index}`}
            >

              {/* Section heading for multi-issue responses */}
              {proposals.length > 1 && (
                <h3 className="zi-issue-heading">
                  <span className="zi-number">
                    {index + 1}
                  </span>
                  {item.issue}
                </h3>
              )}

              {/* Main complaint statistic */}
              {item.metrics?.mentions != null && (
                <div className="zi-stat">

                  <strong>
                    {item.metrics.mentions}
                  </strong>

                  <div>
                    <span className="zi-stat-label">
                      FEEDBACK RECORDS
                    </span>

                    <span className="zi-stat-description">
                      Mentioning {item.issue.toLowerCase()}
                    </span>
                  </div>

                </div>
              )}

              {/* Finding for multi-issue responses */}
              {proposals.length > 1 && (
                <p className="zi-paragraph zi-finding">
                  {item.finding}
                </p>
              )}

              {/* Recommended product action */}
              <div className="zi-section">

                <h3 className="zi-section-heading">
                  <CheckCircle2 size={17} />
                  Recommended product improvement
                </h3>

                <p className="zi-action">
                  {item.action}
                </p>

              </div>

              {/* Business reasoning */}
              <div className="zi-section">

                <h3 className="zi-section-heading">
                  Why this makes sense
                </h3>

                <p className="zi-paragraph">
                  {item.rationale}
                </p>

              </div>

              {/* Customer evidence */}
              {item.sources?.length > 0 && (
                <div className="zi-section">

                  <h3 className="zi-section-heading">
                    <BookOpenCheck size={17} />
                    Supporting customer evidence
                  </h3>

                  <div className="zi-evidence-list">

                    {item.sources.map((source, i) => (

                      <button
                        type="button"
                        key={`${source.source_id}-${i}`}
                        className="zi-evidence"
                        onClick={() => onSource(source.source_id)}
                      >

                        <span className="zi-quote">
                          “{source.quote}”
                        </span>

                        <span className="zi-source">
                          <span>
                            {source.source_id}
                            {' · '}
                            {source.source_type?.replaceAll('_', ' ')}
                            {' · '}
                            {source.date}
                          </span>

                          <ChevronRight size={15} />
                        </span>

                      </button>

                    ))}

                  </div>
                </div>
              )}

              {/* Success metrics */}
              {item.success_metrics?.length > 0 && (
                <div className="zi-section">

                  <h3 className="zi-section-heading">
                    How to measure success
                  </h3>

                  <ul className="zi-metric-list">

                    {item.success_metrics.map((metric, i) => (
                      <li key={i}>
                        {metric}
                      </li>
                    ))}

                  </ul>

                </div>
              )}

            </section>

          ))}
        </>
      )}

    </article>
  )
}


// Show the original customer record when clicked
function SourceDrawer({ id, close }) {

  const [record, setRecord] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {

    setRecord(null)
    setError('')

    api(`/sources/${encodeURIComponent(id)}`)
      .then(setRecord)
      .catch(error => setError(error.message))

  }, [id])

  return (
    <div className="drawer-backdrop" onClick={close}>

      <aside
        className="source-drawer"
        onClick={event => event.stopPropagation()}
      >

        <div className="drawer-head">
          <div>
            <span className="eyebrow">
              ORIGINAL CUSTOMER EVIDENCE
            </span>
            <h2>{id}</h2>
          </div>

          <button className="icon-btn" onClick={close}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className="alert">{error}</div>
        )}

        {record ? (
          <>
            <div className="source-meta">

              <div>
                <span>Source type</span>
                <strong>
                  {record.source_type?.replaceAll('_', ' ')}
                </strong>
              </div>

              <div>
                <span>Recorded</span>
                <strong>{record.feedback_date}</strong>
              </div>

              <div>
                <span>Rating</span>
                <strong>{record.rating ?? 'N/A'}</strong>
              </div>

            </div>

            <h3>Original feedback record</h3>

            <p className="source-body">
              {record.text}
            </p>

            <div className="source-footer">
              <CheckCircle2 size={16} />
              Retrieved from PostgreSQL using the original source ID.
            </div>
          </>
        ) : (
          !error && (
            <p className="muted">
              Loading customer evidence…
            </p>
          )
        )}

      </aside>
    </div>
  )
}


// Main Zipro AI Product Copilot
export default function Copilot() {

  const [threadId, setThreadId] = useState(
    () => sessionStorage.getItem('zipro_active_thread') || newThreadId()
  )

  const [conversations, setConversations] = useState(
    () => {
      try {
        return JSON.parse(
          sessionStorage.getItem('zipro_thread_list') || '[]'
        )
      } catch {
        return []
      }
    }
  )

  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [sourceId, setSourceId] = useState(null)

  const bottomRef = useRef(null)

  useEffect(() => {
    sessionStorage.setItem('zipro_active_thread', threadId)
  }, [threadId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])


  // Ask the AI Product Copilot
  async function ask(value) {

    const text = (value || question).trim()

    if (!text || loading) return

    setQuestion('')
    setLoading(true)

    setMessages(old => [
      ...old,
      { role: 'user', text }
    ])

    try {

      const result = await api('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: text,
          thread_id: threadId
        })
      })

      setMessages(old => [
        ...old,
        {
          role: 'assistant',
          answer: result.answer
        }
      ])

      if (!conversations.includes(threadId)) {

        const next = [
          threadId,
          ...conversations
        ].slice(0, 15)

        setConversations(next)

        sessionStorage.setItem(
          'zipro_thread_list',
          JSON.stringify(next)
        )
      }

    } catch (error) {

      setMessages(old => [
        ...old,
        {
          role: 'assistant',
          answer: {
            status: 'error',
            message: error.message
          }
        }
      ])

    } finally {
      setLoading(false)
    }
  }


  // Start a new conversation
  function newChat() {

    setThreadId(newThreadId())
    setMessages([])
    setQuestion('')
  }


  // Open previous conversation
  async function openThread(id) {

    if (loading) return

    setThreadId(id)
    setMessages([])

    try {

      const result = await api(`/history/${id}`)

      setMessages(
        result.messages.map(item => (
          item.role === 'human'
            ? { role: 'user', text: item.content }
            : { role: 'assistant', answer: item.content }
        ))
      )

    } catch {
      setMessages([])
    }
  }


  return (
    <div className="copilot-page">

      {/* Scoped presentation styles */}
      <style>{`
        .zi-answer {
          width: 100%;
          max-width: 820px;
          padding: 25px;
          background: #fff;
          border: 1px solid #e5eaf0;
          border-radius: 16px;
          color: #26364b;
          font-size: 13.5px;
          line-height: 1.85;
          overflow-wrap: anywhere;
        }

        .zi-answer * {
          box-sizing: border-box;
        }

        .zi-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          flex-wrap: wrap;
          margin-bottom: 21px;
        }

        .zi-brand {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          color: #526b89;
          font-size: 11px;
          font-weight: 750;
          letter-spacing: .6px;
        }

        .zi-verified {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 5px 10px;
          background: #edf8f2;
          color: #26754e;
          border-radius: 30px;
          font-size: 10px;
          font-weight: 700;
        }

        .zi-main-title {
          margin: 0 0 13px;
          font-size: 20px;
          line-height: 1.4;
          font-weight: 750;
          color: #193654;
        }

        .zi-intro {
          margin: 0 0 22px;
          font-size: 14.5px;
          line-height: 1.9;
          font-weight: 500;
          color: #304761;
        }

        .zi-proposal {
          padding: 0 0 26px;
          margin: 0 0 26px;
          border-bottom: 1px solid #edf0f4;
        }

        .zi-proposal:last-of-type {
          border-bottom: none;
          margin-bottom: 5px;
        }

        .zi-issue-heading {
          display: flex;
          align-items: center;
          gap: 10px;
          color: #183654;
          font-size: 16px;
          font-weight: 750;
          margin: 0 0 17px;
        }

        .zi-number {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 25px;
          height: 25px;
          flex-shrink: 0;
          background: #edf3fa;
          border-radius: 8px;
          color: #355a83;
          font-size: 12px;
        }

        .zi-stat {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 13px 17px;
          margin-bottom: 20px;
          background: #f7f9fc;
          border: 1px solid #e6edf5;
          border-radius: 12px;
        }

        .zi-stat strong {
          color: #183b65;
          font-size: 27px;
          line-height: 1;
          font-weight: 750;
        }

        .zi-stat > div {
          display: flex;
          flex-direction: column;
          gap: 3px;
        }

        .zi-stat-label {
          color: #70849c;
          font-size: 10px;
          font-weight: 750;
          letter-spacing: .5px;
        }

        .zi-stat-description {
          font-size: 12px;
          color: #536c87;
        }

        .zi-paragraph {
          margin: 0 0 12px;
          line-height: 1.95;
          color: #35465c;
        }

        .zi-finding {
          font-weight: 500;
        }

        .zi-section {
          margin-top: 23px;
        }

        .zi-section-heading {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 0 0 10px;
          color: #1b3859;
          font-size: 13.5px;
          line-height: 1.5;
          font-weight: 750;
        }

        .zi-section-heading svg {
          color: #6486ac;
          flex-shrink: 0;
        }

        .zi-action {
          margin: 0;
          color: #243a54;
          font-weight: 550;
          line-height: 1.95;
        }

        .zi-evidence-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .zi-evidence {
          display: block;
          width: 100%;
          padding: 15px 17px;
          border: 1px solid #e4ebf3;
          border-radius: 11px;
          background: #f8fafc;
          text-align: left;
          cursor: pointer;
          font: inherit;
          transition: background .15s, border-color .15s;
        }

        .zi-evidence:hover {
          background: #f0f5fb;
          border-color: #c7d7e9;
        }

        .zi-quote {
          display: block;
          font-size: 13px;
          font-style: italic;
          line-height: 1.85;
          color: #354c66;
        }

        .zi-source {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          margin-top: 10px;
          color: #5c7ba0;
          font-size: 11px;
          font-weight: 650;
        }

        .zi-metric-list {
          margin: 0;
          padding-left: 22px;
          color: #34485f;
        }

        .zi-metric-list li {
          padding-left: 3px;
          margin: 7px 0;
          line-height: 1.8;
        }

        .zi-metric-list li::marker {
          color: #6587ad;
        }

        @media (max-width: 600px) {
          .zi-answer {
            padding: 17px;
          }

          .zi-main-title {
            font-size: 18px;
          }

          .zi-stat {
            padding: 12px;
          }
        }
      `}</style>

      <div className="page-heading copilot-header">

        <div>
          <div className="eyebrow">
            PRODUCT DECISION WORKSPACE
          </div>

          <h1>AI product copilot</h1>

          <p>
            Investigate customer experiences and make
            evidence-backed product decisions.
          </p>
        </div>

        <button className="outline-button" onClick={newChat}>
          <Plus size={17} />
          New conversation
        </button>

      </div>

      <div className="copilot-layout">

        <div className="chat-container">

          <div className="chat-top">

            <div>
              <span className="active-circle" />

              <strong>
                Zipro intelligence assistant
              </strong>

              <span className="chat-version">
                Hybrid RAG + evidence checks
              </span>
            </div>

            <span className="chat-thread">
              Session {threadId.slice(0, 8)}
            </span>

          </div>

          <div className="chat-scroll">

            {messages.length === 0 && (

              <div className="chat-welcome">

                <div className="welcome-icon">
                  <Sparkles size={26} />
                </div>

                <h2>
                  What would you like to investigate?
                </h2>

                <p>
                  Explore customer complaints, investigate
                  recurring problems, or discuss product priorities.
                </p>

                <div className="suggestion-grid">

                  {SUGGESTIONS.map(item => (

                    <button
                      key={item}
                      onClick={() => ask(item)}
                    >

                      <span>{item}</span>

                      <ArrowUpRight size={16} />

                    </button>

                  ))}

                </div>

              </div>
            )}

            {messages.map((message, index) => (

              message.role === 'user' ? (

                <div className="user-message" key={index}>
                  {message.text}
                </div>

              ) : (

                <div className="assistant-message" key={index}>

                  <div className="assistant-avatar">
                    <Sparkles size={16} />
                  </div>

                  <VerifiedAnswer
                    answer={message.answer}
                    onSource={setSourceId}
                  />

                </div>
              )
            ))}

            {loading && (

              <div className="loading-agent">
                <LoaderCircle size={18} className="spin" />

                <span>
                  Analyzing customer feedback…
                </span>
              </div>

            )}

            <div ref={bottomRef} />

          </div>

          <form
            className="chat-composer"
            onSubmit={event => {
              event.preventDefault()
              ask()
            }}
          >

            <textarea
              value={question}
              onChange={event => setQuestion(event.target.value)}
              placeholder="Ask about customer feedback or product decisions…"
              rows={2}
              onKeyDown={event => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  ask()
                }
              }}
            />

            <div className="composer-footer">

              <span>
                <ShieldCheck size={14} />
                Evidence-backed product intelligence
              </span>

              <button
                type="submit"
                disabled={!question.trim() || loading}
                className="send-button"
                aria-label="Send message"
              >
                <Send size={19} />
              </button>

            </div>

          </form>

        </div>

        <aside className="copilot-side">

          <div className="side-heading">
            <History size={17} />
            Conversations
          </div>

          <p className="side-note">
            Continue previous investigations and explore follow-up questions.
          </p>

          <button className="side-new" onClick={newChat}>
            <Plus size={16} />
            Start a new conversation
          </button>

          <div className="thread-list">

            {conversations.map(id => (

              <button
                className={id === threadId ? 'selected' : ''}
                key={id}
                onClick={() => openThread(id)}
              >
                <MessagesSquare size={15} />
                Conversation {id.slice(0, 8)}
              </button>

            ))}

          </div>

          <div className="side-footer">

            <ShieldCheck size={18} />

            <div>
              <strong>Evidence rules enabled</strong>

              <span>
                Original customer feedback is checked before citations appear.
              </span>
            </div>

          </div>

        </aside>

      </div>

      {sourceId && (
        <SourceDrawer
          id={sourceId}
          close={() => setSourceId(null)}
        />
      )}

    </div>
  )
}
