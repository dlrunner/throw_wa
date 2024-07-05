import React, { createContext, useState } from 'react'
import axios from 'axios'

export const AppContext = createContext();

const AppContextProvider = (props) => {
  const [posts, setPosts] = useState([]);  

  const getPosts = async () => {
    const response = await axios('/api/posts');
    console.log(response);
    setPosts(response.data);
  }
  const getPost = async (id) => {
    return await axios(`/api/posts/${id}`);
  }
  const createMember = async (post) => {
    return await axios.post('http://localhost:8080/api/signUp', post);
  }

  const value = {
    state: {
      posts
    },
    action: {
      getPosts,
      getPost,
      createMember
    }
  };

  return (
    <AppContext.Provider value={value}>
      {props.children}
    </AppContext.Provider>
  )
}

export default AppContextProvider