package java_client_grafic;

import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import java.math.BigInteger;


public class Controller {

    @FXML private TextField messageInput, ipInput, nicknameInput;
    @FXML private TextArea messageArea;
    @FXML private Label connectedLabel;

    private ClientRSA clientRSA;
    private boolean connected=false;

    @FXML
    private void initialize() {
        connectedLabel.setText("Currently not connected!");
        messageArea.setStyle(" -fx-background: -fx-control-inner-background ;\n" +
                "    -fx-background-color: -fx-table-cell-border-color, -fx-background ;\n" +
                "    -fx-background-insets: 0, 0 0 1 0 ;\n" +
                "    -fx-table-cell-border-color: derive(-fx-color, 0%);");
    }

    @FXML
    private void connectToServer(){

        if(nicknameInput.getText().length() == 0) {
            nicknameInput.setStyle("-fx-background-color: red");
            connected=false;
            connectedLabel.setText("Currently not connected!");
            return;
        }

        clientRSA = new ClientRSA();
        if(!(clientRSA.runClient(ipInput.getText(), nicknameInput.getText()))) {
            nicknameInput.setStyle("-fx-background-color: green");
            ipInput.setStyle("-fx-background-color: red"); //couldnt connect to server
            clientRSA.setCurrentlyConnected(false);
            connected=false;
            connectedLabel.setText("Currently not connected!");
        } else {
            ipInput.setStyle("-fx-background-color: green"); //success connecting...
            nicknameInput.setStyle("-fx-background-color: green");
            clientRSA.setCurrentlyConnected(true);
            connected=false;
            connectedLabel.setText("Currently connected to \"" + ipInput.getText() + "\"");

            new Thread(() -> {
                while (true) {
                    if(!clientRSA.getCurrentlyConnected())
                        break;
                    String s = clientRSA.getMessage(), text = "";
                    if(s.length() <= 2)
                        continue;

                    String nums[] = s.substring(s.indexOf("[") + 1, s.indexOf("]")).split(",");

                    for (int i = 0; i < nums.length; i++) {
                        BigInteger encrypted = clientRSA.base36Decoder(nums[i].substring(nums[i].indexOf("\"") + 1, nums[i].lastIndexOf("\"")));
                        BigInteger decrypted = clientRSA.modularesPotenzieren(encrypted, clientRSA.getPrivateKey(), clientRSA.getN());
                        text += String.valueOf((char) (decrypted.intValue()));
                    }
                    messageArea.appendText("\n" + text);
                    if(!clientRSA.getCurrentlyConnected())
                        break;

                }
            }).start();
        }

    }

    @FXML
    private void sendMessage(){

        if(connected && messageInput.getLength() > 0) {
            clientRSA.sendUserMessage(messageInput.getText());
            messageInput.setText("");
        }
    }
    @FXML
    public void stopConnection() {
        if(connected) {
            clientRSA.stopConnection();
            clientRSA.setCurrentlyConnected(false);
            connected = false;
            connectedLabel.setText("Currently not connected!");
        }
    }

    @FXML
    public void onEnter(){ //handle enter key on messageInput
        if(messageInput.getLength() > 0)
            sendMessage();
    }

}
