"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { RegisterForm } from "@/components/register-form";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const res = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    if (res.ok) {
      alert("Account created. You can now log in.");
      router.push("/login");
    } else {
      const err = await res.json();
      alert(err.detail || "Registration failed");
    }
  };

  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <RegisterForm
          name={name}
          email={email}
          password={password}
          onNameChange={setName}
          onEmailChange={setEmail}
          onPasswordChange={setPassword}
          onSubmit={handleRegister}
        />
      </div>
    </div>
  );
}
