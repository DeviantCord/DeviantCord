import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import java.io.FileReader;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.nio.file.Paths;
import java.util.Properties;
import java.util.Scanner;

public class DBInsertTest {

    public static void main(String[] args)
    {
        System.out.println("NOTE: THIS IS AN PROTOTYPE, DO NOT USE FOR PRODUCTION USE");
        System.out.println("Written by Errite Games LLC, 2021");
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
          System.out.println("Please enter the serverid");
          Scanner serverid = new Scanner(System.in);
          long obt_serve = serverid.nextLong();
          System.out.println("Please enter the roleid");
          Scanner roleid = new Scanner(System.in);
          long obt_role = roleid.nextLong();
          props.put("dataSource.logWriter", new PrintWriter(System.out));
          System.out.println("Test");
          String test_sql = "INSERT INTO deviantcord.server_config(serverid, prefix, errite_optout, required_role, updated) VALUES \n" +
                  "(?, ?, ?, ?, default)";
          Connection testcon = ds.getConnection();
            try (PreparedStatement pstmt = testcon.prepareStatement(test_sql)) {
                // use pstmt here
                pstmt.setLong(1,obt_serve);
                pstmt.setString(2, "$$");
                pstmt.setBoolean(3, false);
                pstmt.setLong(4, obt_role);
                pstmt.executeUpdate();
            }
            testcon.close();
        }
        catch (Exception e) {
            e.printStackTrace();
        }

    }
}
