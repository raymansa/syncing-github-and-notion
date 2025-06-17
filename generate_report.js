import { Client } from '@notionhq/client';
import dotenv from 'dotenv';
import fs from 'fs';

// TODO: Add Agile and Sprint reporting to the report 

// Load environment variables
dotenv.config();

// Initialize Notion client
const notion = new Client({ auth: process.env.NUEROFLUX_KEY });

// Database IDs
const CRM_DB_ID = process.env.CRM_DB_ID;
const STAKEHOLDER_DB_ID = process.env.STAKEHOLDER_DB_ID;
const PROJECTS_DB_ID = process.env.PROJECTS_DB_ID;
const TASKS_DB_ID = process.env.TASKS_DB_ID;
const MEETING_NEXT_STEPS_DB_ID = process.env.MEETING_NEXT_STEPS_DB_ID;
const EMPLOYEE_DB_ID = process.env.NUEROFLUX_PEOPLE_DB_ENV;

/**
 * Extract value from a Notion property based on its type
 * @param {Object} property - Notion property object
 * @returns {string} Formatted property value
 */
function getPropertyValue(property) {
  if (!property) return '';
  switch (property.type) {
    case 'title':
      return property.title.map(t => t.text.content).join('');
    case 'rich_text':
      return property.rich_text.map(rt => rt.text.content).join('');
    case 'select':
      return property.select?.name || '';
    case 'multi_select':
      return property.multi_select.map(ms => ms.name).join(', ');
    case 'date':
      return property.date?.start || '';
    case 'number':
      return property.number?.toString() || '';
    case 'checkbox':
      return property.checkbox ? 'Yes' : 'No';
    case 'relation':
      return property.relation.map(r => r.id).join(', ');
    case 'people':
      return property.people.map(p => p.name).join(', ');
    default:
      return 'Unknown';
  }
}

/**
 * Retrieve CRM data
 * @returns {Promise<Array>} Array of customer objects
 */
async function getCRMData() {
  try {
    const response = await notion.databases.query({
      database_id: CRM_DB_ID,
    });
    
    let crmData = response.results.map(page => ({
      customerName: getPropertyValue(page.properties['Company Name']),
      crmPhase: getPropertyValue(page.properties['CRM Phase']),
      meetingNextSteps: getPropertyValue(page.properties['Meeting Next Steps']),
      initialProjectIdea: getPropertyValue(page.properties['Initial Project Idea']),
    }));
    return crmData
  } catch (error) {
    console.error('Error fetching CRM data:', error.body || error.message);
    return [];
  }
}

/**
 * Retrieve Stakeholders data with Next Steps from NfxDB_Meeting Next Steps
 * @returns {Promise<Array>} Array of stakeholder objects with resolved next steps
 */
async function getStakeholdersData() {
  try {
    // Query Stakeholders database
    const stakeholdersResponse = await notion.databases.query({
      database_id: STAKEHOLDER_DB_ID,
    });
    // Query NfxDB_Meeting Next Steps database
    const nextStepsResponse = await notion.databases.query({
      database_id: MEETING_NEXT_STEPS_DB_ID,
    });

    // Map Meeting Next Steps ID to their Next Steps text
    const nextStepsMap = new Map();
    nextStepsResponse.results.forEach(page => {
      const next_steps = getPropertyValue(page.properties['Next Steps']);
      nextStepsMap.set(page.id, next_steps);
    });


    // Build stakeholder data with resolved next steps
    return stakeholdersResponse.results.map(page => {
      const nextStepIds = page.properties['Next Steps']?.relation?.map(r => r.id) || [];
      const nextStepsTexts = nextStepIds.map(id => nextStepsMap.get(id) || '');
      return {
        name: getPropertyValue(page.properties['Stakeholder Name']),
        stakeholderPhase: getPropertyValue(page.properties['Stakeholder Phase']),
        purpose: getPropertyValue(page.properties['Purpose']),
        nextSteps: nextStepsTexts.join('; ') || 'N/A',
      };
    });
  } catch (error) {
    console.error('Error fetching Stakeholders data:', error.body || error.message);
    return [];
  }
}

/**
 * Retrieve Projects data
 * @returns {Promise<Array>} Array of project objects
 */
async function getProjectsData() {
  try {
    const response = await notion.databases.query({
      database_id: PROJECTS_DB_ID,
    });
    const customers = await notion.databases.query({
      database_id: CRM_DB_ID,
    });

    return Promise.all(response.results.map(async page => {
      const customerIds = page.properties['Customer']?.relation?.map(r => r.id) || [];

      const customerNameMap = new Map()
      customers.results.forEach(page => {
          const id = page.id
          const name = getPropertyValue(page.properties['Company Name'])
          customerNameMap.set(id, name)
      })
  
      const customerText = customerIds.map(id => customerNameMap.get(id) || 'No Company Contracted');
  
      return {
        name: getPropertyValue(page.properties['Project Name']),
        customer: customerText.join('; ') || 'No Company Contracted',
        stage: getPropertyValue(page.properties['Stage']) || '0. Not Started',
        project_status: getPropertyValue(page.properties['Project Status']) || 'No Status',
        process_step: getPropertyValue(page.properties['Process Step']) || 'No steps taken'
      };
    })
    )

  } catch (error) {
    console.error('Error fetching Projects data:', error.body || error.message);
    return [];
  }
}

/**
 * Retrieve Tasks data
 * @returns {Promise<Array>} Array of task objects
 */
async function getTasksData() {
  try {
    const response = await notion.databases.query({
      database_id: TASKS_DB_ID,
    });
    const employees = await notion.databases.query({
        database_id: EMPLOYEE_DB_ID,
      })
    const stakeholders = await notion.databases.query({
        database_id: STAKEHOLDER_DB_ID,
      })
    const customers = await notion.databases.query({
        database_id: CRM_DB_ID,
      })
    return Promise.all(response.results.map(async page => {
      const responsibleIds = page.properties['Responsible']?.relation?.map(r => r.id) || [];
      const entityIds = page.properties['Stakeholder']?.relation?.map(r => r.id) || page.properties['Customer']?.relation?.map(r => r.id) || [];

      const responsibleNamesMap = new Map()
      employees.results.forEach(page => {
        const id = page.id
        const name = getPropertyValue(page.properties['First Name'])
        responsibleNamesMap.set(id, name)
      })

      const entityNamesMap = new Map()
      stakeholders.results.forEach(page => {
        const id = page.id
        const name = getPropertyValue(page.properties['Stakeholder Name'])
        entityNamesMap.set(id, name)
      })
      customers.results.forEach(page => {
        const id = page.id
        const name = getPropertyValue(page.properties['Company Name'])
        entityNamesMap.set(id, name)
      })
      
      const responsibleText = responsibleIds.map(id => responsibleNamesMap.get(id) || '');
      const entityText = entityIds.map(id => entityNamesMap.get(id) || '');
      const taskData =  {
        title: getPropertyValue(page.properties['Title']),
        entity_name: entityText.join('; ') || 'No Entity Name',
        responsible: responsibleText.join('; ') || 'No person assigned',
        plannedEnd: getPropertyValue(page.properties['Planned_End']) || 'No planned end date',
        status: page.properties.Status.status.name || "No Status Set",
        importance: getPropertyValue(page.properties.Importance),
        priority: getPropertyValue(page.properties.Priority)
      };

      return taskData
    }));
  } catch (error) {
    console.error('Error fetching Tasks data:', error.body || error.message);
    return [];
  }
}

/**
 * Generate HTML report
 */
async function generateReport() {
  const crmData = await getCRMData();
  const stakeholdersData = await getStakeholdersData();
  const projectsData = await getProjectsData();
  const tasksData = await getTasksData();

  // --- Grouping Function ---
  const groupData = (data, key) => {
    return data.reduce((acc, item) => {
      const groupKey = item[key] || '0. No engagement';
      if (!acc[groupKey]) {
        acc[groupKey] = [];
      }
      acc[groupKey].push(item);
      return acc;
    }, {});
  };

  const crmDataByPhase = groupData(crmData, 'crmPhase');
  const stakeholdersDataByPhase = groupData(stakeholdersData, 'stakeholderPhase');
  const projectsDataByStage = groupData(projectsData, 'stage');

  // --- **NEW** HTML Generation Function for Column-Based Table ---
  const generateStyledTableHtml = (groupedData, cardGenerator) => {
    const sortedGroupNames = Object.keys(groupedData).sort();
    let html = '<table class="kanban-table">';

    // Create the header row with category names
    html += '<thead><tr>';
    for (const groupName of sortedGroupNames) {
      html += `<th>${groupName}</th>`;
    }
    html += '</tr></thead>';

    // Create the body row with a cell for each column
    html += '<tbody><tr>';
    for (const groupName of sortedGroupNames) {
      html += '<td class="kanban-column">';
      // Place all cards for that group in the cell
      html += groupedData[groupName].map(cardGenerator).join('');
      html += '</td>';
    }
    html += '</tr></tbody>';
    html += '</table>';
    return html;
  };
  
  const crmCardGenerator = item => `
    <div class="kanban-card">
      <div class="card-title">${item.customerName || 'N/A'}</div>
      <p class="card-detail"><strong>Next Steps:</strong> ${item.meetingNextSteps || 'N/A'}</p>
      <p class="card-detail"><strong>Project Idea:</strong> ${item.initialProjectIdea || 'N/A'}</p>
    </div>
  `;

  const stakeholderCardGenerator = item => `
    <div class="kanban-card">
      <div class="card-title">${item.name || 'N/A'}</div>
      <p class="card-detail"><strong>Purpose:</strong> ${item.purpose || 'No purpose defined'}</p>
      <p class="card-detail"><strong>Next Steps:</strong> ${item.nextSteps || 'No next step set'}</p>
    </div>
  `;

  const generateProjectStatusHtml = (status) => {
    let color = '#585858'; // Default color
    switch (status) {
        case "Potential": color = '#660099'; break;
        case "Active":    color = '#3300FF'; break;
        case "On Hold":   color = '#CC9900'; break;
        case "Blocked":   color = '#680000'; break;
        case "Completed": color = '#00FF00'; break;
    }
    return `<p class="card-detail"><strong>Project Status:</strong> <span style="color: ${color};">${status || 'N/A'}</span></p>`;
  };

  const projectCardGenerator = item => `
    <div class="kanban-card">
      <div class="card-title">${item.name || 'N/A'}</div>
      <p class="card-detail"><strong>Customer:</strong> ${item.customer || 'N/A'}</p>
      <p class="card-detail"><strong>Process Step:</strong> ${item.process_step || 'N/A'}</p>
      ${generateProjectStatusHtml(item.project_status)}
    </div>
  `;


  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project Status Report</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f0f2f5;
      color: #333;
    }
    h1, h2 {
      color: #172b4d;
      padding-bottom: 10px;
      border-bottom: 1px solid #dfe1e6;
    }
    h2 {
      margin-top: 40px;
    }

    /* New Kanban Table Styles */
    .kanban-table {
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      margin-bottom: 20px;
    }
    .kanban-table th {
      background-color: #f4f5f7;
      font-weight: 600;
      color: #42526e;
      padding: 15px;
      text-align: left;
      border: 1px solid #dfe1e6;
    }
    .kanban-column {
      vertical-align: top;
      padding: 10px;
      border: 1px solid #dfe1e6;
    }
    .kanban-column > .kanban-card {
      margin-bottom: 15px;
    }
    .kanban-column > .kanban-card:last-child {
      margin-bottom: 0;
    }

    /* Card styles (retained) */
    .kanban-card {
      background-color: #ffffff;
      border-radius: 5px;
      padding: 15px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    }
    .card-title {
      font-weight: 600;
      margin-bottom: 10px;
    }
    .card-detail {
      font-size: 14px;
      color: #5e6c84;
      margin: 5px 0;
    }
    .card-detail strong {
      color: #42526e;
    }

    /* Original Table Styles for Tasks */
    .tasks-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
      background-color: #fff;
    }
    .tasks-table th, .tasks-table td {
      border: 1px solid #ddd;
      padding: 12px;
      text-align: left;
    }
    .tasks-table th {
      background-color: #f2f2f2;
      color: #2c3e50;
    }
    .tasks-table tr:nth-child(even) {
      background-color: #f9f9f9;
    }

    .title-page {
        height: 90vh;
        background: url(pictures/project_planning1.jpg);
        background-repeat: no-repeat;
        background-size: cover;
        padding: 2rem;
    }

    .title-page p {
      color: #001728
    }
    
    
    @media print {
      body {
        margin: 0;
        padding: 0;
        size: A4 portrait;
        background-color: #fff;
      }
      h1 {
        page-break-after: avoid;
      }
      h2 {
        page-break-before: always; /* Each section starts on a new page */
        page-break-after: avoid;
      }
      h2:first-of-type {
        page-break-before: auto; /* Avoid page break before the first h2 */
      }
      .kanban-table, .tasks-table {
        page-break-inside: auto;
      }
      .kanban-card {
        page-break-inside: avoid; /* Do not break a card across pages */
        box-shadow: none;
        border: 1px solid #ddd;
      }
      
    }
  </style>
</head>
<body>
  <div class="title-page">
    <h1>Project Status Report</h1>
    <p>Generated on: ${new Date().toLocaleString('en-ZA', { timeZone: 'Africa/Johannesburg' })}</p>
  </div>
  
  <h2>Customers</h2>
  ${generateStyledTableHtml(crmDataByPhase, crmCardGenerator)}

  <h2>Stakeholders</h2>
  ${generateStyledTableHtml(stakeholdersDataByPhase, stakeholderCardGenerator)}

  <h2>Projects</h2>
  ${generateStyledTableHtml(projectsDataByStage, projectCardGenerator)}

  <h2>Tasks</h2>
  <table class="tasks-table">
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
      ${tasksData.map(item => `
        <tr>
          <td>${item.title || 'No task title'}</td>
          <td>${item.entity_name || 'No entity Name' }</td>
          <td>${item.responsible || 'No person assigned'}</td>
          <td>${item.plannedEnd || 'No deadline set'}</td>
          <td>${item.status || 'No Status'}</td>
        </tr>
      `).join('')}
    </tbody>
  </table>
</body>
</html>
  `;

  fs.writeFileSync('report.html', html);
  console.log('Report generated: report.html');
}

// Run the report generation
generateReport().catch(console.error);