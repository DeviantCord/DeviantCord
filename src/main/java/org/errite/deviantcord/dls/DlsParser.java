package org.errite.deviantcord.dls;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.parsing.Parser;
import io.restassured.response.Response;

import static io.restassured.RestAssured.given;
/*
 * NOTE: DLS has been deprecated in favor of moving all of the functionality directly into the bot.
 *       This class will remain for now, but will be removed in a future version.
 */

public class DlsParser {

    public static Response GetToken(String hostname, String username, String password)
    {
        RestAssured.defaultParser = Parser.JSON;
        String TokenRequestUrl = hostname + "/get_token/" + username + "/" + password + "/deviantcord";
        System.out.println(TokenRequestUrl);
        Response dls_response = given().headers("Content-Type", ContentType.JSON, "Accept", ContentType.JSON).
                when().get(TokenRequestUrl).
                then().contentType(ContentType.JSON).extract().response();
        return dls_response;

    }

    public static Response GetShardResponse(String hostname, String token, String shard_type)
    {
        String ShardRequestUrl = hostname + "/get_shard/" + token + "/" + shard_type;
        System.out.println(ShardRequestUrl);
        Response dls_response = given().headers("Content-Type", ContentType.JSON, "Accept", ContentType.JSON).
                when().get(ShardRequestUrl).
                then().contentType(ContentType.JSON).extract().response();
        return dls_response;
    }
}
