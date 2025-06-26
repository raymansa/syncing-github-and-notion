import React from 'react';
import KanbanCard from './KanbanCard'; // Assuming KanbanCard.js exists

/**
 * A generic component to render a full Kanban board with columns.
 * @param {object} props
 * @param {string} props.title - The main title for the board section (e.g., "Projects Status").
 * @param {Array} props.items - The array of items to display (e.g., data.projects).
 * @param {string} props.groupByKey - The key in each item object to group by (e.g., "stage").
 * @param {Function} props.getCardDetails - A function that maps an item to the details object for the card.
 * @param {Function} props.getCardStatusClass - A function that maps an item to its status class.
 */
const KanbanBoard = ({ title, items, groupByKey, getCardDetails, getCardStatusClass }) => {
    
    // Group items into columns based on the groupByKey
    const columns = items.reduce((acc, item) => {
        const key = item[groupByKey] || 'Uncategorized';
        if (!acc[key]) {
            acc[key] = [];
        }
        acc[key].push(item);
        return acc;
    }, {});

    const sortedColumnKeys = Object.keys(columns).sort();

    return (
        <div className="content-section">
            <h3>{title}</h3>
            <div className="kanban-board">
                {sortedColumnKeys.map(columnName => (
                    <div key={columnName} className="kanban-column">
                        <h3>{columnName}</h3>
                        {columns[columnName].map(item => (
                            <KanbanCard
                                key={item.id}
                                title={item.project_name || item.company_name || item.title}
                                statusClass={getCardStatusClass(item)}
                                details={getCardDetails(item)}
                            />
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default KanbanBoard;