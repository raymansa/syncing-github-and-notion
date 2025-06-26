import React, { useState, useEffect } from 'react';
import { getLogs } from '../services/apiService';

const LogsView = () => {
    const [logsData, setLogsData] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        getLogs()
            .then(data => setLogsData(data))
            .catch(err => setError(err.message));
    }, []);

    const getStatusPill = (status) => {
        const lowerStatus = status.toLowerCase();
        return <span className={`log-pill ${lowerStatus}`}>{`[${status}]`}</span>;
    };

    if (error) return <div>Error fetching logs: {error}</div>;
    if (!logsData) return <div>Loading logs...</div>;

    return (
        <div>
            <h2>Sync Logs</h2>
            <div className="sync-summary">
                {/* This data would eventually come from an API endpoint */}
                <p><strong>Last Successful Sync:</strong> October 26, 2023, 06:00:15 AM</p>
                <p><strong>Next Scheduled Sync:</strong> October 26, 2023, 12:00:00 PM</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Service</th>
                        <th>Action</th>
                        <th>Details</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {logsData.logs.map((log, index) => (
                        <tr key={index}>
                            <td>{new Date(log.timestamp).toLocaleString()}</td>
                            <td>{log.service}</td>
                            <td>{log.action}</td>
                            <td>{log.details}</td>
                            <td>{getStatusPill(log.status)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default LogsView;