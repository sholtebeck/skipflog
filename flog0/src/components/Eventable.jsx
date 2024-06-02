import { useState, useMemo } from 'react'
import { sortRows, filterRows, paginateRows, pickResults } from './helpers'
import { Pagination } from './Pagination'
import PickersTable from './PickersTable';
import Button from "react-bootstrap/Button";
//import Table from 'react-bootstrap/Table';

export function Eventable({ columns, rows, pageSize }) {
    const [activePage, setActivePage] = useState(1)
    const [filters, setFilters] = useState({})
    const [sort, setSort] = useState({ order: 'asc', orderBy: 'rank' })
    const rowsPerPage = Number(pageSize)||20;

    const filteredRows = useMemo(() => filterRows(rows, filters), [rows, filters])
    const sortedRows = useMemo(() => sortRows(filteredRows, sort), [filteredRows, sort])
    const calculatedRows = paginateRows(sortedRows, activePage, rowsPerPage)
    const count = filteredRows.length
    const totalPages = Math.ceil(count / rowsPerPage)
    const totalColumns = columns.length
    const headerName = "Events:"

    const handleSearch = (value, accessor) => {
        setActivePage(1)

        if (value) {
            setFilters((prevFilters) => ({
                ...prevFilters,
                [accessor]: value,
            }))
        } else {
            setFilters((prevFilters) => {
                const updatedFilters = { ...prevFilters }
                delete updatedFilters[accessor]

                return updatedFilters
            })
        }
    }

    const handleSort = (accessor) => {
        setActivePage(1)
        setSort((prevSort) => ({
            order: prevSort.order === 'asc' && prevSort.orderBy === accessor ? 'desc' : 'asc',
            orderBy: accessor,
        }))
        
    }

    const clearAll = () => {
        setSort({ order: 'desc', orderBy: 'ID' })
        setActivePage(1)
        setFilters({})
        // clear inputs
        Array.from(document.querySelectorAll("input")).forEach(
            input => (input.value = "")
          );
        //handleClear();
    }

    return (
        <>
        <div> 
            <h5> <b>Event: </b> 
        <input
            className="input-filter"
            key="name-search"
            type="search"
            placeholder="Event Name"
            value={filters["name"]}
            onChange={(event) => handleSearch(event.target.value, "name")} />
                    <Button variant="dark" onClick={clearAll}>Clear</Button></h5>
            </div>
            <table className="table-sm event-table">
                <thead>
                    <tr className="heading">
                        {columns.map((column) => {
                            const sortIcon = () => {
                                if (column.accessor === sort.orderBy) {
                                    if (sort.order === 'asc') {
                                        return '↓'
                                    }
                                    return '↑'
                                } else {
                                    return '️'
                                } 
                            }
                            return (
                                <th className="table-header"
                                    key={column.accessor}>
                                   <span onClick={() => handleSort(column.accessor)}>{column.label}
                                   {sortIcon()}  </span>                              </th>
                            )
                        })}
                    </tr>
                </thead>
                <tbody>
                    {calculatedRows.map((row) => {
                        return (
                            <tr key={row.name}>
                                {columns.map((column) => {
                                    if (column.fixed) {
                                        return <td className="table-data-left" key={column.accessor}>{row[column.accessor].toFixed(column.fixed)}</td>
                                    }                                  
                                    return <td className="table-data-left" key={column.accessor}>{row[column.accessor]}</td>
                                })}
                            </tr>
                        )
                    })}
</tbody>
<tfoot>
            {totalPages > 0 && (
              <Pagination
                    activePage={activePage}
                    count={count}
                    rowsPerPage={rowsPerPage}
                    totalPages={totalPages}
                    setActivePage={setActivePage} 
                    totalColumns={totalColumns}
					headerName={headerName}
                 />
            ) 
            }
</tfoot>
</table>
<p /><PickersTable pickers={pickResults(filteredRows)} /> 
        </>
    )
}