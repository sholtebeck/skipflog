const PointsTable = ({ pickers }) => (
    <table className="points-table">
    <thead>
      <tr><th className="table-border">Rank</th>
          <th className="table-border">Picker</th>	
          <th className="table-border">Count</th>	
          <th className="table-border">Points</th>
         </tr>
    </thead>
   <tbody>
   {pickers.map(picker => (
            <tr key={picker.rank}>
               <td className="table-data">{picker.rank}</td>
               <td className="table-data">{picker.name}</td>
               <td className="table-data">{picker.count}</td>
               <td className="table-data">{picker.points}</td>
             </tr>
    ))}
    </tbody>
  </table>
);

export default PointsTable;