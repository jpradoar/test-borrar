output "connection" {
  value       = "ssh -i 'kp/${aws_key_pair.demo_sshkey_tf.key_name}' admin@${aws_instance.ec2_instance.public_dns}"
}