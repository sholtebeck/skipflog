import { useState, useMemo } from 'react'
import { sortRows, filterRows, paginateRows } from './helpers'
import { Pagination } from './Pagination'
import Button from "react-bootstrap/Button";

export function Datatable({ columns, rows, pageSize, canPick, handlePick, setPlayer }) {
    const [activePage, setActivePage] = useState(1)
    const [filters, setFilters] = useState({})
    const [sort, setSort] = useState({ order: 'asc', orderBy: 'rank' })
    const rowsPerPage = Number(pageSize)||20;

    const filteredRows = useMemo(() => filterRows(rows, filters), [rows, filters])
    const sortedRows = useMemo(() => sortRows(filteredRows, sort), [filteredRows, sort])
    const calculatedRows = paginateRows(sortedRows, activePage, rowsPerPage)

    const count = filteredRows.length
    const totalPages = Math.ceil(count / rowsPerPage)
    const totalColumns = columns.length + 1

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
        setSort({ order: 'asc', orderBy: 'rank' })
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
            <h5> <b>Available Players:</b> 
        <input
            key="name-search"
            type="search"
            placeholder="Search Name"
            value={filters["name"]}
            onChange={(event) => handleSearch(event.target.value, "name")} />
                    <Button variant="dark" onClick={clearAll}>Clear</Button></h5>
            </div>
            <table className="table table-sm">
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
                        {handlePick && <th className="table-header">Action</th> }
                    </tr>
                </thead>
                <tbody>
                    {calculatedRows.map((row) => {
                        return (
                            <tr key={row.name}>
                                {columns.map((column) => {
                                    if (column.format) {
                                        return <td key={column.accessor}>{column.format(row[column.accessor])}</td>
                                    }                                  
                                    return <td key={column.accessor}>{row[column.accessor]}</td>
                                })}
                                { canPick ?
                                <td>
                                <Button variant="dark"
                                onClick={() => setPlayer(row.name)}>Select</Button>                             
                                </td> : <td><Button variant="secondary" disabled>Pick</Button></td>
                        }

                            </tr>
                        )
                    })}
</tbody>
<tfoot>
            {totalPages > 1 && (
              <Pagination
                    activePage={activePage}
                    count={count}
                    rowsPerPage={rowsPerPage}
                    totalPages={totalPages}
                    setActivePage={setActivePage} 
                    totalColumns={totalColumns}
                 />
            ) 
            }
</tfoot>
</table>

        </>
    )
}