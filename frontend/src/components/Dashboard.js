import React, { useState, useEffect } from 'react';
import { getDashboardData } from '../services/apiService';
// import KanbanCard from './KanbanCard';

// Reusable components for clarity
const KanbanCard = ({ title, details, statusClass }) => (
    <div className={`kanban-card ${statusClass}`}>
        <strong>{title}</strong>
        {Object.entries(details).map(([key, value]) => (
            <p key={key} className="card-detail"><strong>{key}:</strong> {value}</p>
        ))}
    </div>
);

const Dashboard = ({ activeView, onLogout, onNavigate, setFlashMessage }) => {
    const [data, setData] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const dashboardData = await getDashboardData();
                console.log("Dashboard data:", dashboardData); 
                setData(dashboardData);
            } catch (err) {
                setError(err.message);
                if (err.message.includes('Unauthorized')) {
                    if (setFlashMessage) {
                        setFlashMessage('Session expired or invalid. Please log in again.');
                    }
                    onLogout && onLogout('Session expired or invalid. Please log in again.'); 
                }
                if (err.message.includes('Failed to fetch dashboard data')) {
                    if (setFlashMessage) {
                        setFlashMessage('An error has occured. Please log in again.');
                    }
                    onLogout && onLogout('An error has occured. Please log in again.'); 
                }
            }
        };
        fetchData();
    }, [onLogout, setFlashMessage]);

    if (error) return <div className="mockup-container">Error: {error}</div>;
    if (!data) return <div className="mockup-container">Loading...</div>;

    // Helper: group customers by crm_phase
    const customerPhases = Array.from(new Set(data.customers?.map(c => c.crm_phase)));
    // Helper: group stakeholders by phase
    const stakeholderPhases = Array.from(new Set(data.stakeholders?.map(s => s.stakeholder_phase)));
    // Helper: group projects by stage
    const projectStages = Array.from(new Set(data.projects?.map(p => p.stage)));

    return (
        <div className="main-app-container">
            
            <header className="app-header">
                <div className="header-content">
                    <h1>Nueroflux Project Admin</h1>
                    <nav>
                        <a href="#dashboard" onClick={(e) => onNavigate(e, 'dashboard')} className={activeView === 'dashboard' ? 'active' : ''}>Dashboard</a>
                        <a href="#report" onClick={(e) => onNavigate(e, 'report')} className={activeView === 'report' ? 'active' : ''}>Weekly Status Report</a>
                        <a href="#logs" onClick={(e) => onNavigate(e, 'logs')} className={activeView === 'logs' ? 'active' : ''}>Sync Logs</a>
                    </nav>
                    <div className="header-controls">
                        <button className="btn btn-primary">Generate & Share PDF</button>
                        <button className="btn btn-secondary" onClick={onLogout}>Logout</button>
                    </div>
                </div>
            </header>

            <div className="mockup-container">
                <div id="dashboard" className={`section ${activeView === 'dashboard' ? 'active' : ''}`}>
                    <h2>Dashboard</h2>

                    <div className="content-section">
                        <h3>Projects Status</h3>
                        <div className="kanban-board">
                            {projectStages.map(stage => (
                                <div className="kanban-column" key={stage}>
                                    <h3>{stage}</h3>
                                    {data.projects
                                        .filter(p => p.stage === stage)
                                        .map(p => (
                                            <KanbanCard
                                                key={p.id}
                                                title={p.project_name}
                                                details={{
                                                    "Process Step": p.description,
                                                    "Project Status": p.status
                                                }}
                                                statusClass={
                                                    p.stage === "Planning & Design"
                                                        ? "status-warning"
                                                        : p.stage === "Execution (Active)"
                                                        ? "status-info"
                                                        : p.stage === "On Hold / Blocked"
                                                        ? "status-danger"
                                                        : ""
                                                }
                                            />
                                        ))}
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="content-section">
                        <h3>Customers (CRM Pipeline)</h3>
                        <div className="kanban-board">
                            {customerPhases.map(phase => (
                                <div className="kanban-column" key={phase}>
                                    <h3>{phase}</h3>
                                    {data.customers
                                        .filter(c => c.crm_phase === phase)
                                        .map(c => (
                                            <KanbanCard
                                                key={c.id}
                                                title={c.company_name}
                                                details={{
                                                    "Project Idea": c.initial_project_idea,
                                                    "Next Step": c.next_step_summary
                                                }}
                                                statusClass="status-info"
                                            />
                                        ))}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Stakeholders (SRM Pipeline) */}
                    <div className="content-section">
                        <h3>Stakeholders (SRM Pipeline)</h3>
                        <div className="kanban-board">
                            {stakeholderPhases.map(phase => (
                                <div className="kanban-column" key={phase}>
                                    <h3>{phase}</h3>
                                    {data.stakeholders
                                        .filter(s => s.stakeholder_phase === phase)
                                        .map(s => (
                                            <KanbanCard
                                                key={s.id}
                                                title={s.stakeholder_name}
                                                details={{
                                                    Next: s.next_step_summary,
                                                    Purpose: s.purpose
                                                }}
                                                statusClass="status-info"
                                            />
                                        ))}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Task List */}
                    <div className="content-section">
                        <h3>Task List</h3>
                        <div className="filter-bar">
                            <select>
                                <option>Filter by Project...</option>
                            </select>
                            <select>
                                <option>Filter by Status...</option>
                            </select>
                        </div>
                        <table>
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Entity</th>
                                    <th>Responsible</th>
                                    <th>Planned End</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.tasks.map(task => (
                                    <tr key={task.id}>
                                        <td>{task.title}</td>
                                        <td>{task.entity_name}</td>
                                        <td>{task.responsible_name}</td>
                                        <td>{task.planned_end_date}</td>
                                        <td>
                                            <span className={
                                                task.status === "Done"
                                                    ? "status-pill pill-success"
                                                    : task.status === "In Progress"
                                                    ? "status-pill pill-warning"
                                                    : "status-pill pill-todo"
                                            }>
                                                {task.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                </div>

                <div id="report" className={`section ${activeView === 'report' ? 'active' : ''}`}>
                    <div id="pdf-report" className="weekly-report">
                        <div className="pdf-header">
                            <h2>Weekly Status Report</h2>
                            <p>Generated on: {new Date().toLocaleString()}</p>
                        </div>
                        <div className="pdf-section">

                            {/* 1. Project Status */}
                            <h3>1. Project Status</h3>
                            {data.projects.map((proj, idx) => (
                                <div key={idx} className="report-section">
                                    <h4>Stage: {proj.stage}</h4>
                                    <h5>{proj.project_name}</h5>
                                    <div className="report-project-details">
                                        <p>Project Manager: {proj.manager}</p>
                                        <p>Customer: {proj.customer}</p>
                                        <p>Status: {proj.status}</p>
                                        <p>Process Step: {proj.process_step}</p>
                                    </div>
                                    {proj.characteristics && proj.characteristics.length > 0 && (
                                        <table className="report-table">
                                            <thead>
                                                <tr>
                                                    <th>Quality Characteristics</th>
                                                    <th>Features</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {proj.characteristics.map((row, i) => (
                                                    <tr key={i}>
                                                        <td>{row.quality}</td>
                                                        <td>
                                                            <ul>
                                                                {row.features.map((f, j) => <li key={j}>{f}</li>)}
                                                            </ul>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    )}
                                </div>
                            ))}

                            {/* 2. Customer Pipeline */}
                            <h3>2. Customer Pipeline</h3>
                            {data.customers.map((cust, idx) => (
                                <div key={idx} className="report-section">
                                    <h4>Phase: {cust.crm_phase}</h4>
                                    <h5>{cust.company_name}</h5>
                                    <table className="report-table">
                                        <thead>
                                            <tr>
                                                <th>Project Idea</th>
                                                <th>Status</th>
                                                <th>Tasks</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>{cust.initial_project_idea}</td>
                                                <td>{cust.status}</td>
                                                <td>{cust.next_step_summary}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            ))}

                            {/* 3. Stakeholder Pipeline */}
                            <h3>3. Stakeholder Pipeline</h3>
                            {data.stakeholders.map((s, idx) => (
                                <div key={idx} className="report-section">
                                    <h4>Phase: {s.stakeholder_phase}</h4>
                                    <h5>{s.stakeholder_name}</h5>
                                    <table className="report-table">
                                        <thead>
                                            <tr>
                                                <th>Purpose</th>
                                                <th>Status</th>
                                                <th>Tasks</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>{s.purpose}</td>
                                                <td>{s.status}</td>
                                                <td>{s.next_step_summary}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            ))}

                            {/* 4. Key Upcoming Tasks */}
                            <h3>4. Key Upcoming Tasks</h3>
                            <table className="report-table">
                                <thead>
                                    <tr>
                                        <th>Task Title</th>
                                        <th>TaskType</th>
                                        <th>Entity</th>
                                        <th>Responsible</th>
                                        <th>Important and Not Urgent</th>
                                        <th>Priority</th>
                                        <th>Due Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.tasks.map((t, idx) => (
                                        <tr key={idx}>
                                            <td>{t.title}</td>
                                            <td>{t.type}</td>
                                            <td>{t.entity_name}</td>
                                            <td>{t.responsible_name}</td>
                                            <td>{t.important}</td>
                                            <td>{t.priority}</td>
                                            <td>{t.planned_end_date}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div id="logs" className={`section ${activeView === 'logs' ? 'active' : ''}`}>
                    <h2>Sync Logs</h2>
                    <table className="sync-log-table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Message</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.sync_logs && data.sync_logs.length > 0 ? (
                                data.sync_logs.map(log => (
                                    <tr key={log.id}>
                                        <td>{log.timestamp}</td>
                                        <td>{log.message}</td>
                                        <td>
                                            <span className={
                                                log.status === "success"
                                                    ? "status-pill pill-success"
                                                    : log.status === "error"
                                                    ? "status-pill pill-failure"
                                                    : "status-pill"
                                            }>
                                                {log.status.charAt(0).toUpperCase() + log.status.slice(1)}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3">No sync logs available.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;