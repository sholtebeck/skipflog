const PointsTable = ({ pickers }) => (
    <table className="points-table">
    <thead>
      <tr><th className="table-header">Rank</th>
          <th className="table-header">Picker</th>	
          <th className="table-header">Count</th>	
          <th className="table-header">Points</th>
         </tr>
    </thead>
   <tbody>
   {pickers.map(picker => (
            <tr key={picker.Rank}>
               <td>{picker.Rank}</td>
               <td>{picker.Name}</td>
               <td>{picker.Count}</td>
               <td>{picker.Points}</td>
             </tr>
    ))}
    </tbody>
  </table>
);

export default PointsTable;