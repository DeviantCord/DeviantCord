import java.util.Random;

public class testRandom {
     public static void main(String[] args) {
         Random rand = new Random();
         char[] chars = new char[8];
         for(int i=0;i<chars.length;i++) {
             chars[i] = (char) rand.nextInt(65536);
             if (!Character.isValidCodePoint(chars[i]))
                 i--;
         }
         String s = new String(chars);
         System.out.println(s);
    }
}
