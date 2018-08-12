import React, { Component } from "react";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      message: "Loading...",
    };
  }

  componentDidMount() {
    fetch("http://localhost:5000/")
      .then(response => response.json())
      .then(data => {
        this.setState({ message: data.message });
      });
  }

  render() {
    return <div>{this.state.message}</div>;
  }
}

export default App;
