import org.errite.deviantcord.sd.commandIdParser;


public class testParsePageString {

    public static void main(String[] args) {
        String test_id = "np-58845483838";
        String result = commandIdParser.parsePageString(test_id);
        System.out.println(result);
    }
}
