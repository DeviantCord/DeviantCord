import org.errite.deviantcord.sd.commandIdParser;

public class DebugCommandIdParser {

    public static void main(String[] args) {

        String testCommandId = "ui576555243299405824FI-:-SHINY-COBRAFI-:-PMD: WHITE ROSEFI-:-";
        commandIdParser.parseNonChannelReplaceString(testCommandId);

    }
}
