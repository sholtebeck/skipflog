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

  export function pickPlayer(eventInfo,playerName) {
    let player="";
	  let turn=[0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1]
	  let ord=["First","Second","Third","Fourth","Fifth","Sixth","Seventh","Eighth","Ninth","Tenth","Alt"]
	  for (let p=0; p<eventInfo.players.length; p++) {
		  if (eventInfo.players[p].name == playerName && eventInfo.players[p].picked == 0) { 	eventInfo.players[p].picked=1; player=playerName;	}
	  }
	  if (player) {
	    for (let p=0; p<eventInfo.pickers.length; p++) { 
			 if (eventInfo.pickers[p].name == eventInfo.next && eventInfo.pickers[p].picks.indexOf(player)==-1) { 
			if (eventInfo.pick_no<=20) { eventInfo.pickers[p].picks.push(player); } else { eventInfo.pickers[p].altpick=player; }
			} 
		}
    if (eventInfo.pick_no>1 && eventInfo.lastpick[0] == eventInfo.next[0]) {
		  eventInfo.lastpick+=" and "+playerName
		} else {
			eventInfo.lastpick=eventInfo.next+" picked "+player
		}
		if (eventInfo.pick_no < turn.length) {
			let t=turn[eventInfo.pick_no]
			let n=eventInfo.pickers[t].picks.length;
			eventInfo.next=eventInfo.pickers[t].name;
			eventInfo.nextpick=eventInfo.next+"'s "+ord[n]+" Pick";
			eventInfo.pick_no+=1;
		  } else {
		    eventInfo.next=eventInfo.nextpick="Pau";
		  } 
    }
	return eventInfo;
}
  