package handlers

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

type Post struct {
	Logger *log.Logger
}

type Message struct {
	Message string `json:"message"`
}

func NewPost(logger *log.Logger) *Post {
	return &Post{logger}
}


func (post *Post) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK) // 200 OK

	fileContent, err := os.Open("message.json")

	if err != nil {
	   log.Fatal(err)
	   return
	}
 
	fmt.Println("The File is opened successfully...")
 
	defer fileContent.Close()

   byteResult, _ := ioutil.ReadAll(fileContent)

   var message Message

   json.Unmarshal(byteResult, &message)   
	post.Logger.Println(message.Message)	
}