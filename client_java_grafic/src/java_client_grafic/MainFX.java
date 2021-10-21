package java_client_grafic;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;
import java.util.Objects;

public class MainFX extends Application {

    @Override
    public void start(Stage primaryStage) throws Exception{
        Parent root = FXMLLoader.load(Objects.requireNonNull(getClass().getResource("sample.fxml")));
        primaryStage.setTitle("RSA Client in Java");
        primaryStage.setScene(new Scene(root, 320, 500));
        primaryStage.setMinWidth(332);
        primaryStage.setMinHeight(300);
        primaryStage.getIcons().add(new Image("file:logo_client.jpg"));
        primaryStage.show();
    }


    public static void main(String[] args) {
        launch(args);
    }
}
