const ResultsTable = ({ pickers }) => (
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
               <td>{picker.rank}</td>
               <td>{picker.name}</td>
               <td>{(picker.points).toFixed(2)}</td>
               <td>{picker.wins}</td>
               <td>{picker.losses}</td>
               <td>{(100*picker.wins/(picker.wins+picker.losses)).toFixed(2)}</td>
               <td>{(picker.points/(picker.wins+picker.losses)).toFixed(2)}</td>
             </tr>
    ))}
    </tbody>
  </table>


);

export default ResultsTable;