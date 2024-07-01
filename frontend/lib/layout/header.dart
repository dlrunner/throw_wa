import 'package:flutter/material.dart';

AppBar buildAppBar(BuildContext context) {
  return AppBar(
    backgroundColor: Theme.of(context).colorScheme.inversePrimary,
    leading: IconButton(
      icon: Icon(Icons.menu),
      onPressed: () {
        // 메뉴 아이콘 클릭 시 수행할 동작
        print('Menu icon pressed');
      },
    ),
    title: Text('Flutter Demo Home Page'),
    actions: <Widget>[
      TextButton(
        onPressed: () {
          // 로그인 버튼 클릭 시 수행할 동작
          print('Login button pressed');
        },
        child: Text(
          'Login',
          style: TextStyle(color: Colors.white),
        ),
      ),
    ],
  );
}