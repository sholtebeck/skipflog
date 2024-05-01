const PickersTable = ({ pickers }) => (
    <table className="results-table">
    <thead>
      <tr><th className="table-header">Rank</th>
          <th className="table-header">Picker</th>	
          <th className="table-header">Points</th>	
          <th className="table-header">Wins</th>	
          <th className="table-header">Losses</th>
          <th className="table-header">Win Pct</th>
          <th className="table-header">Avg Pts</th>
    </tr>
    </thead>
   <tbody>
   {pickers.map(picker => (
            <tr key={picker.rank}>
               <td className="table-data">{picker.rank}</td>
               <td className="table-data">{picker.name}</td>
               <td className="table-data">{picker.points}</td>
               <td className="table-data">{picker.wins}</td>
               <td className="table-data">{picker.losses}</td>
               <td className="table-data">{(100*picker.wins/(picker.wins+picker.losses)).toFixed(2)}</td>
               <td className="table-data">{(picker.points/(picker.wins+picker.losses)).toFixed(2)}</td>
             </tr>
    ))}
    </tbody>
  </table>


);

export default PickersTable;