package remoteDriver;

import net.sourceforge.jFuzzyLogic.FIS;
import net.sourceforge.jFuzzyLogic.rule.Rule;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Locale;
import java.util.StringTokenizer;
 
public class RemoteDriver {
	
	static int port = 4321;
	static String host = "localhost";
	
    public static void main(String[] args) throws IOException {
        	    	
        Socket kkSocket = null;
        PrintWriter out = null;
        BufferedReader in = null;

        FIS fis = FIS.load(RemoteDriver.class.getClassLoader().getResourceAsStream("remoteDriver.fcl"), true);

        // Error while loading?
        if( fis == null ) {
            System.err.println("Can't load file");
            return;
        }
        while (out == null && in == null) {
            try {
                kkSocket = new Socket(host, port);
                out = new PrintWriter(kkSocket.getOutputStream(), true);
                in = new BufferedReader(new InputStreamReader(kkSocket.getInputStream()));
                break;
            } catch (UnknownHostException e) {
                System.err.println("Don't know about host:" + host);
            } catch (IOException e) {
                System.err.println("Couldn't get I/O for the connection to: " + host);
            }
            try {
                Thread.sleep(1000);
            } catch(InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
 
        String fromServer;
 
        double x, y;
        double angle;

        // requisicao da posicao do caminhao
        out.println("r");
        while ((fromServer = in.readLine()) != null) {
        	StringTokenizer st = new StringTokenizer(fromServer);
        	x = Double.valueOf(st.nextToken()).doubleValue();
        	y = Double.valueOf(st.nextToken()).doubleValue();
        	angle = Double.valueOf(st.nextToken()).doubleValue();

        	System.out.println("x: " + x + " y: " + y + " angle: " + angle);
            System.out.printf(Locale.ENGLISH, "To see graphics, run in the project folder: java -jar lib/jFuzzyLogic.jar -e resources/remoteDriver.fcl %f %f %f\n", angle, x, y);
        	
            // Set inputs
            fis.setVariable("x", x);
            fis.setVariable("y", y);
            fis.setVariable("direction", angle);

            // Evaluate
            fis.evaluate();


        	double respostaDaSuaLogica = fis.getVariable("angle").getValue(); // atribuir um valor entre -1 e 1 para virar o volante pra esquerda ou direita.

        	System.out.printf("Command sent: %f\n", respostaDaSuaLogica);

            // Show each rule (and degree of support)
            for( Rule r : fis.getFunctionBlock("remoteDriver").getFuzzyRuleBlock("No1").getRules() ) {
                if (r.getDegreeOfSupport() == 0.0) {
                    continue;
                }
                System.out.println(r);
            }
            System.out.println("----------------------------");
        	
        	///////////////////////////////////////////////////////////////////////////////// Acaba sua modificacao aqui
        	// envio da acao do volante
        	out.println(respostaDaSuaLogica);
        	
            // requisicao da posicao do caminhao        	
        	out.println("r");	
        }
 
        out.close();
        in.close();
        kkSocket.close();
    }
}