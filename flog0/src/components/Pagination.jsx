import React from 'react';
//import button from "react-bootstrap/button";

export const Pagination = ({ activePage, count, rowsPerPage, totalPages, setActivePage, totalColumns, headerName }) => {
    const beginning = activePage === 1 ? 1 : rowsPerPage * (activePage - 1) + 1
    const end = activePage === totalPages ? count : beginning + rowsPerPage - 1
  
    return (
      <tr className="heading" key="footer">
          <td colSpan={totalColumns}>
          <label className="left">
          { activePage === 1 ? <div><button variant="secondary" disabled>First</button> <button variant="secondary" disabled>Prev</button></div>
             : <div><button variant="dark" onClick={() => setActivePage(1)}>First</button> <button variant="dark" onClick={() => setActivePage(activePage - 1)}>Prev</button></div>
          }
          </label>{headerName} {beginning === end ? end : `${beginning} - ${end}`} of {count}    
          <label className="right">
        { activePage === totalPages ? <div>Page: {activePage} of {totalPages} <button variant="secondary" disabled>Next</button> <button variant="secondary" disabled>Last</button></div> 
        : <div>Page: {activePage} of {totalPages} <button variant="dark" onClick={() => setActivePage(activePage + 1)}>Next</button> <button variant="dark" onClick={() => setActivePage(totalPages)}>Last</button></div>
        }
        </label>
       </td>
       </tr>
     )
  }