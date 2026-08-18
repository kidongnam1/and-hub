#!/data/data/com.termux/files/usr/bin/bash
# Termux Widget 원터치 홈 화면 아이콘 자동 생성 스크립트

mkdir -p ~/.shortcuts

cat << 'EOF' > ~/.shortcuts/중복정리_대화형.sh
#!/data/data/com.termux/files/usr/bin/bash
cd ~/and-hub && git pull origin main && bash dedup.sh all-ask
EOF

cat << 'EOF' > ~/.shortcuts/중복정리_자동.sh
#!/data/data/com.termux/files/usr/bin/bash
cd ~/and-hub && git pull origin main && bash dedup.sh all
EOF

cat << 'EOF' > ~/.shortcuts/중복정리_원상복구.sh
#!/data/data/com.termux/files/usr/bin/bash
cd ~/and-hub && bash dedup.sh restore
EOF

chmod +x ~/.shortcuts/*.sh
echo "[완료] 스마트폰 홈 화면 위젯용 스크립트 3개가 등록되었습니다."
echo "이제 스마트폰 바탕화면에서 [위젯 추가] -> [Termux:Widget]을 선택하여 아이콘을 놓으시면 됩니다!"
