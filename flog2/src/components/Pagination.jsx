import React from 'react';
import Button from "react-bootstrap/Button";

export const Pagination = ({ activePage, count, rowsPerPage, totalPages, setActivePage, totalColumns }) => {
    const beginning = activePage === 1 ? 1 : rowsPerPage * (activePage - 1) + 1
    const end = activePage === totalPages ? count : beginning + rowsPerPage - 1
  
    return (
      <tr className="heading" key="footer">
          <td colSpan="6">
          <label className="left">
          { activePage === 1 ? <div><Button variant="secondary" disabled>First</Button> <Button variant="secondary" disabled>Prev</Button></div>
             : <div><Button variant="dark" onClick={() => setActivePage(1)}>First</Button> <Button variant="dark" onClick={() => setActivePage(activePage - 1)}>Prev</Button></div>
          }
          </label> Players: {beginning === end ? end : `${beginning} - ${end}`} of {count}    
          <label className="right">
        { activePage === totalPages ? <div>Page: {activePage} of {totalPages} <Button variant="secondary" disabled>Next</Button> <Button variant="secondary" disabled>Last</Button></div> 
        : <div>Page: {activePage} of {totalPages} <Button variant="dark" onClick={() => setActivePage(activePage + 1)}>Next</Button> <Button variant="dark" onClick={() => setActivePage(totalPages)}>Last</Button></div>
        }
        </label>
       </td>
       </tr>
     )
  }