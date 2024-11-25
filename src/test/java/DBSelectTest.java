import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import java.io.FileReader;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;

public class DBSelectTest {
    public static void main(String[] args){
        System.out.println("Written by Errite Games LLC");
        JSONParser dbconfigparser = new JSONParser();
        Path currentPath = Paths.get(System.getProperty("user.dir"));
        Path dbConfigPath = Paths.get(currentPath.toString(),"db.json");
        System.out.println(dbConfigPath.toString());
        try{
            Object obj = dbconfigparser.parse(new FileReader(dbConfigPath.toString()));
            JSONObject jsonObject = (JSONObject) obj;
            String host = (String) jsonObject.get("database-host");
            String username = (String) jsonObject.get("database-username");
            String password = (String) jsonObject.get("database-password");
            String port = String.valueOf(jsonObject.get("database-port"));
            String database_name = (String) jsonObject.get("database-name");
            Properties props = new Properties();

            props.setProperty("dataSourceClassName", "org.postgresql.ds.PGSimpleDataSource");
            props.setProperty("dataSource.user", username);
            props.setProperty("dataSource.password", password);
            props.setProperty("dataSource.serverName", host);
            props.setProperty("dataSource.portNumber", port);
            props.setProperty("dataSource.databaseName", database_name);
            HikariConfig config = new HikariConfig(props);
            HikariDataSource ds = new HikariDataSource(config);
            String test_sql = "SELECT * from deviantcord.deviation_notifications where inverse = false";
            Connection testcon = ds.getConnection();
            Statement stmt = testcon.createStatement();
            ResultSet rs = stmt.executeQuery(test_sql);
            while (rs.next()){
                long channel_id = rs.getLong("channelid");
                System.out.println(channel_id);
            }
        }
        catch (Exception e) {
            e.printStackTrace();
        }
    }
}
