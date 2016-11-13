package remoteDriver;

import net.sourceforge.jFuzzyLogic.FIS;
import net.sourceforge.jFuzzyLogic.rule.Variable;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
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
 
        try {
            kkSocket = new Socket(host, port);
            out = new PrintWriter(kkSocket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(kkSocket.getInputStream()));
        } catch (UnknownHostException e) {
            System.err.println("Don't know about host:"  + host);
            System.exit(1);
        } catch (IOException e) {
            System.err.println("Couldn't get I/O for the connection to: " + host);
            System.exit(1);
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
        	
        	/////////////////////////////////////////////////////////////////////////////////////
        	// TODO sua lógica fuzzy vai aqui use os valores de x,y e angle obtidos. x e y estao em [0,1] e angulo [0,360)
        	
        	
        	
			
        	// double teste = Double.valueOf(stdIn.readLine());



            // Set inputs
            fis.setVariable("x", x);
            fis.setVariable("y", y);
            fis.setVariable("angle", angle);

            // Evaluate
            fis.evaluate();

            Variable result = fis.getVariable("result");
        	
        	
        	double respostaDaSuaLogica = result.getValue(); // atribuir um valor entre -1 e 1 para virar o volante pra esquerda ou direita.
            if (respostaDaSuaLogica == result.getUniverseMax()) {
                respostaDaSuaLogica = 1;
            }
            if (respostaDaSuaLogica == result.getUniverseMin()) {
                respostaDaSuaLogica = -1;
            }
        	System.out.printf("Command sent: %f\n", respostaDaSuaLogica);
        	
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