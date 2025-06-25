import React from 'react';

/**
 * A reusable card component for display within a Kanban board column.
 * It accepts a title, a status class for styling, and an object of
 * details to be displayed as key-value pairs.
 *
 * @param {object} props - The component's properties.
 * @param {string} props.title - The main title of the card.
 * @param {string} props.statusClass - The CSS class for the left-border color (e.g., 'status-warning').
 * @param {object} props.details - An object where each key-value pair is rendered as a detail line.
 */
const KanbanCard = ({ title, statusClass, details }) => {
  return (
    // The main div combines a base class with a dynamic status class for styling.
    <div className={`kanban-card ${statusClass}`}>
      
      {/* The title is displayed prominently in bold. */}
      <strong>{title}</strong>

      {/* 
        We iterate over the 'details' object. This makes the card highly flexible.
        It can display any number of detail lines without changing the component itself.
      */}
      {Object.entries(details).map(([key, value]) => (
        <p key={key} className="card-detail">
          <strong>{key}:</strong> {value || 'N/A'}
        </p>
      ))}
    </div>
  );
};

export default KanbanCard;