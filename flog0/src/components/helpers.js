// Helper functions for Datatable
export function isEmpty(obj = {}) {
    return Object.keys(obj).length === 0
  }
  
  export function isString(value) {
    return typeof value === 'string' || value instanceof String
  }
  
  export function isNumber(value) {
    return typeof value == 'number' && !isNaN(value)
  }
  
  export function isBoolean(value) {
    return value === true || value === false
  }
  
  export function isNil(value) {
    return typeof value === 'undefined' || value === null
  }
  
  export function isDateString(value) {
    if (!isString(value)) return false
  
    return value.match(/^\d{2}-\d{2}-\d{4}$/)
  }
  
  export function convertDateString(value) {
    return value.substr(6, 4) + value.substr(3, 2) + value.substr(0, 2)
  }
  
  export function toLower(value) {
    if (isString(value)) {
      return value.toLowerCase()
    }
    return value
  }
  
  export function convertType(value) {
    if (isNumber(value)) {
      return value.toString()
    }
  
    if (isDateString(value)) {
      return convertDateString(value)
    }
  
    if (isBoolean(value)) {
      return value ? '1' : '-1'
    }
  
    return value
  }
  
  export function filterRows(rows, filters) {
    if (isEmpty(filters)) return rows
  
    return rows.filter((row) => {
      return Object.keys(filters).every((accessor) => {
        const value = row[accessor]
        const searchValue = filters[accessor]
  
        if (isString(value)) {
          return toLower(value).includes(toLower(searchValue))
        }
  
        if (isBoolean(value)) {
          return (searchValue === 'true' && value) || (searchValue === 'false' && !value)
        }
  
        if (isNumber(value)) {
          return value === searchValue
        }
  
        return false
      })
    })
  }
  
  export function sortRows(rows, sort) {
    return rows.sort((a, b) => {
      const { order, orderBy } = sort
  
      if (isNil(a[orderBy])) return 1
      if (isNil(b[orderBy])) return -1
  
      const aLocale = convertType(a[orderBy])
      const bLocale = convertType(b[orderBy])
  
      if (order === 'asc') {
        return aLocale.localeCompare(bLocale, 'en', { numeric: isNumber(b[orderBy]) })
      } else {
        return bLocale.localeCompare(aLocale, 'en', { numeric: isNumber(a[orderBy]) })
      }
    })
  }
  
  export function paginateRows(sortedRows, activePage, rowsPerPage) {
    return [...sortedRows].slice((activePage - 1) * rowsPerPage, activePage * rowsPerPage)
  }

  export function getNames (events) {
    var eventNames=[]
    for (let e=0;e<events.length;e++) {
      eventNames.push(events[e].name)
    }
    return eventNames;
  }

  export function pickResults(events) {
    let mark={name:"Mark",points:0,wins:0,losses:0,rank:1}
    let steve={name:"Steve",points:0,wins:0,losses:0,rank:2}
    let pickers=[mark,steve]
    for (const event of events) {
       if (event.winner == mark.name ) {
        mark.points+=event.winner_points
        mark.wins +=1;
        steve.points+=event.loser_points
        steve.losses +=1;
      } else {
        steve.points+=event.winner_points
        steve.wins +=1;
        mark.points+=event.loser_points
        mark.losses +=1;
      }
    }
    mark.points=parseFloat(mark.points.toFixed(2))
    steve.points=parseFloat(steve.points.toFixed(2))
    if (steve.wins > mark.wins)  {
      steve.rank=1;
      mark.rank=2;
      pickers=[steve,mark]
    }
    return pickers
  }

  export function playerResults(events,playerName) {
    var results=[], res={};
     for (const event of events) {
      for (const player of event.players) {
        if (player.name == playerName && player.picker) {
            res={ ...player };
            res.ID=event.ID;
            res.name=event.name;
            res.rownum=results.length;
            results.push(res)
        }
      }
    }
    return results;
  }